# -*- coding: utf-8 -*-
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
#  Created on 21-Oct-2022
#
#  @author: dlytle, tbowers

"""INDI Client Module

This module is part of the Lorax-TNG package, written at Lowell Observatory.

INDI Client -- for communication with INDI-based devices
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
    config : dict
        The configuration dictionary
    """

    def __init__(self, parent, config):
        super().__init__()

        # Define various instance attributes
        self.parent = parent
        self.config = config
        self.blobEvent = threading.Event()
        self.device = None

    def newDevice(self, dp):
        """Emmited when a new device is created from INDI server

        Parameters
        ----------
        dp : _type_
            Pointer to the base device instance
        """
        print(f"Receiving Device... {dp.getDeviceName()}")
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
        if prop_name in self.config["status"]:
            print(f"Storing property: {p.getName()}")
            self.store_prop(p)

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
        if prop_name in self.config["status"]:
            for val in svp:
                self.parent.device_status[val.name] = val.s
            self.parent.get_status_and_broadcast()

    def newNumber(self, nvp):
        """Emmited when a new number value arrives from INDI server

        Parameters
        ----------
        nvp : _type_
            Pointer to a number vector property
        """
        prop_name = nvp.name
        if prop_name in self.config["status"]:
            for val in nvp:
                self.parent.device_status[val.name] = val.value
            self.parent.get_status_and_broadcast()

    def newText(self, tvp):
        """Emmited when a device is deleted from INDI server

        Parameters
        ----------
        tvp : _type_
            Pointer to a text vector property
        """
        prop_name = tvp.name
        if prop_name in self.config["status"]:
            for val in tvp:
                self.parent.device_status[val.name] = val.text
            self.parent.get_status_and_broadcast()

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
        print(f"Property Name: {prop_name}")
        prop_type = prop.getType()
        if prop_name in self.config["status"]:
            if prop_type == 0:
                # Number Type
                temp = prop.getNumber()
                for val in temp:
                    # if val.name in self.config["status"]:
                    self.parent.device_status[val.name] = val.value

            elif prop_type == 1:
                # Switch type
                temp = prop.getSwitch()
                for val in temp:
                    # if val.name in self.config["status"]:
                    self.parent.device_status[val.name] = val.s

            elif prop_type == 2:
                # Text type
                temp = prop.getText()
                for val in temp:
                    # if val.name in self.config["status"]:
                    self.parent.device_status[val.name] = val.text

            elif prop_type == 3:
                # Light type
                temp = prop.getLight()
                for val in temp:
                    # if val.name in self.config["status"]:
                    self.parent.device_status[val.name] = val.text
