# -*- coding: utf-8 -*-
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
#  Created on 21-Oct-2022
#
#  @author: dlytle, tbowers

"""Hardware Client Module

This module is part of the Lorax-TNG package, written at Lowell Observatory.

The various hardware clients needed by LORAX live in this module.  At present,
they are:

1. INDI Client -- for communication with INDI-based devices
"""

# Built-In Libraries
import threading

# 3rd Party Libraries
import PyIndi

# Internal Imports


class IndiClient(PyIndi.BaseClient):
    """The INDI client needed for communication with the INDI server

    The INDI server (indiserver) must be running on the machine to which the
    device of interest is attached.  That machine can be independent of the
    one running the Composite Agent that ultimately calls this class; the
    host machine must be specified in the appropriate Composite Agent
    Configuration File (*.yaml).  On the camera host, run::

        indiserver -m <MB> -v <service1> <service2> ...

    where the ``-m <MB>`` specifies the number of MegaBytes can be in the
    server-client queue before the server kills the client connection.

    For example, the command to run the QHY600M camera with the INDI telescope
    simulator would be::

        indiserver -m 1024 -v indi_simulator_telescope indi_qhy_ccd

    where we allow the server-client queue to be up to 1GB in size to account
    for the frame size of images from this device, and we need both the INDI
    Telescope Simulator and the QHYCCD services to be running.

    Parameters
    ----------
    parent : :class:`SubAgent`
        The SubAgent inherited class that calls the IndiClient.  This is used for
        passing information from the client back up to the parent.
    """

    def __init__(self, parent):
        super().__init__()

        # Define various instance attributes
        self.parent = parent
        self.blobEvent = threading.Event()
        self.device = None
        status = {}

    def newDevice(self, dp):
        """Emmited when a new device is created from INDI server

        Parameters
        ----------
        dp : _type_
            Pointer to the base device instance
        """
        print("Receiving Device... " + dp.getDeviceName())
        self.device = dp
        self.parent.device = dp

    def newProperty(self, p):
        """Emmited when a new property is created for an INDI driver

        Parameters
        ----------
        p : _type_
            Pointer to the Property Container
        """
        # print(dir(p))
        # print("new property " + p.getName() + " for device " + p.getDeviceName())
        # print("type = " + str(p.getType()))
        # Go store the property in the appropriate status dictionary.
        prop_name = p.getName()
        if "CCD" in prop_name or "FILTER" in prop_name:
            self.store_prop(p)
        elif "COOLER" in prop_name:
            # Do something else?
            pass
        elif "DOME" in prop_name or "MOUNT" in prop_name:
            # Placeholder to illustrate other agent types
            pass

    def removeProperty(self, p):
        """Emmited when a property is deleted for an INDI driver

        Parameters
        ----------
        p : _type_
            Pointer to the Property Container to remove
        """

    def newBLOB(self, bp):
        """Emmited when a new BLOB value arrives from INDI server

        Parameters
        ----------
        bp : _type_
            Pointer to filled and process BLOB
        """
        # print("new BLOB ", bp.name)
        self.blobEvent.set()

    def newSwitch(self, svp):
        """Emmited when a new switch value arrives from INDI server

        Parameters
        ----------
        svp : _type_
            Pointer to a switch vector property
        """
        prop_name = svp.name
        prop_type = 1
        prop_dict = {"prop_type": prop_type}
        prop_dict["length"] = len(svp)
        prop_vals = []
        for val in svp:
            prop_vals.append((val.name, val.s))
        prop_dict["vals"] = prop_vals
        self.parent.device_status[prop_name] = prop_dict

    def newNumber(self, nvp):
        """Emmited when a new number value arrives from INDI server

        Parameters
        ----------
        nvp : _type_
            Pointer to a number vector property
        """
        prop_name = nvp.name
        prop_type = 0
        prop_dict = {"prop_type": prop_type}
        prop_dict["length"] = len(nvp)
        prop_vals = []
        for val in nvp:
            prop_vals.append((val.name, val.value))
        prop_dict["vals"] = prop_vals
        self.parent.device_status[prop_name] = prop_dict

    def newText(self, tvp):
        """Emmited when a device is deleted from INDI server

        Parameters
        ----------
        tvp : _type_
            Pointer to a text vector property
        """
        return
        prop_name = tvp.name
        prop_type = 2
        # Text type
        temp = tvp.getText()
        prop_dict = {"prop_type": prop_type}
        prop_dict["length"] = len(temp)
        prop_vals = []
        for val in temp:
            prop_vals.append((val.name, val.text))
        prop_dict["vals"] = prop_vals
        self.parent.device_status[prop_name] = prop_dict

    def newLight(self, lvp):
        """Emmited when a new light value arrives from INDI server

        Parameters
        ----------
        lvp : _type_
            Pointer to a light vector property
        """

    def newMessage(self, dp, messageID):
        """Emmited when a new message arrives from INDI server

        Parameters
        ----------
        dp : _type_
            Pointer to the INDI device the message is sent to
        messageID : _type_
            ID of the message that can be used to retrieve the message from the
            device's messageQueue() function
        """

    def serverConnected(self):
        """Emmited when the server is connected"""

    def serverDisconnected(self, exit_code):
        """Emmited when the server gets disconnected

        Parameters
        ----------
        exit_code : _type_
            0  if client was requested to disconnect from server
            -1 if connection to server is terminated due to remote server
               disconnection
        """

    def store_prop(self, prop):
        """Store a property

        _extended_summary_

        Parameters
        ----------
        prop : _type_
            _description_
        """
        prop_name = prop.getName()
        prop_type = prop.getType()

        if not prop_name in self.parent.device_status:
            if prop_type == 0:
                # Number Type
                temp = prop.getNumber()
                prop_dict = {"prop_type": prop_type}
                prop_dict["length"] = len(temp)
                prop_vals = []
                for val in temp:
                    # print(dir(val))
                    prop_vals.append((val.name, val.value))
                prop_dict["vals"] = prop_vals
                self.parent.device_status[prop_name] = prop_dict
            elif prop_type == 1:
                # Switch type
                temp = prop.getSwitch()
                prop_dict = {"prop_type": prop_type}
                prop_dict["length"] = len(temp)
                prop_vals = []
                for val in temp:
                    # print(dir(val))
                    prop_vals.append((val.name, val.s))
                    # print(val.name)
                prop_dict["vals"] = prop_vals
                self.parent.device_status[prop_name] = prop_dict
            elif prop_type == 2:
                # Text type
                temp = prop.getText()
                # print(len(temp))
                # print(dir(temp[0]))
                prop_dict = {"prop_type": prop_type}
                prop_dict["length"] = len(temp)
                prop_vals = []
                for val in temp:
                    # print(dir(val))
                    prop_vals.append((val.name, val.text))
                # print(val.name)
                prop_dict["vals"] = prop_vals
                self.parent.device_status[prop_name] = prop_dict
                # print(status[prop_name])
            elif prop_type == 3:
                # Light type
                temp = prop.getLight()
                prop_dict = {"prop_type": prop_type}
                prop_dict["length"] = len(temp)
                prop_vals = []
                for val in temp:
                    prop_vals.append((val.name, val.text))
                prop_dict["vals"] = prop_vals
                self.parent.device_status[prop_name] = prop_dict
