# -*- coding: utf-8 -*-
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
#  Created on 08-Sep-2022
#
#  @author: dlytle, tbowers

"""Lorax Agent for the QHY 600M CMOS Camera

This module is part of the Lorax-TNG package, written at Lowell Observatory.

This Agent controls the QHY 600M CMOS camera.  It inherits from both the
CameraAgent and the CoolerAgent, having both functions.

In principle, it could also inherit from the FilterWheelAgent, as it has
integrated functionality control for a filter wheel.  This is not implemented
at this time.

Control of the QHY 600M is accomplished through an INDI interface.  Therefore,
this module includes an IndiClient class needed for communication with the
camera and its included hardware.
"""

# Built-In Libraries
import io
import threading
import time
import sys

# 3rd Party Libraries
import astropy.io.fits
import numpy as np
import PyIndi

# Internal Imports
from CameraAgent import CameraAgent
from CoolerAgent import CoolerAgent


class IndiClient(PyIndi.BaseClient):
    """The INDI client needed for communication with the INDI server

    For the QHY 600M CMOS camera, an indiserver must be running on the machine
    to which the camera is attached.  That machine can be independent of the
    one running the QHY600Agent; the camera host must be specified in the
    ``qhy600_config.yaml`` configuration file.  On the camera host, run::

        indiserver -m 1024 -v indi_simulator_telescope indi_qhy_ccd

    where the ``-m 1024`` specifies the number of megabytes can be in the
    server-client queue before the server kills the client connection (in this
    case, we allow 1GB), and we need both the INDI Telescope Simulator and the
    QHYCCD services to be running.

    Parameters
    ----------
    parent : ``QHY600Agent``
        The Agent class that calls the IndiClient.  This is used for passing
        information from the client back up to the parent.
    """

    def __init__(self, parent):
        super().__init__()

        # Define various instance attributes
        self.parent = parent
        self.blobEvent = threading.Event()
        self.camera = None
        status = {}

    def newDevice(self, dp):
        """Emmited when a new device is created from INDI server

        Parameters
        ----------
        dp : _type_
            Pointer to the base device instance
        """
        print("Receiving Device... " + dp.getDeviceName())
        self.camera = dp
        self.parent.camera = dp

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
        self.parent.camera_status[prop_name] = prop_dict

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
        self.parent.camera_status[prop_name] = prop_dict

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
        self.parent.camera_status[prop_name] = prop_dict

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

        if not prop_name in self.parent.camera_status:
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
                self.parent.camera_status[prop_name] = prop_dict
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
                self.parent.camera_status[prop_name] = prop_dict
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
                self.parent.camera_status[prop_name] = prop_dict
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
                self.parent.camera_status[prop_name] = prop_dict

        # print(status)
        # print("       ")


class QHY600Agent(CameraAgent, CoolerAgent):
    """Lorax Agent for the QHY 600M CMOS Camera

    This is the instantiable device Agent for the QHY 600M CMOS camera.  It
    inherits from both the CameraAgent and CoolerAgent abstract classes, as the
    instrument contains both components.

    Parameters
    ----------
    cfile : ``str``
        The name of the configuration file needed to instantiate this class.
    """

    def __init__(self, cfile):

        # Initialize parent classes and instantiate the IndiClient
        print("in QHY600Agent.init")
        super().__init__(cfile)
        self.indiclient = IndiClient(self)

        # Use the configuration file to connect to the INDI Server
        host = self.config["camera_host"]
        port = self.config["camera_port"]
        print(f"Connecting with server at {host}:{port}")
        self.indiclient.setServer(host, port)
        self.camera_status = {}

        # Ensure we are connected to the INDI server before moving on
        while not self.indiclient.connectServer():
            print("  Waiting on connection to the INDI server...")
            time.sleep(0.5)
        print(f"Connected to INDI Server: {self.indiclient.isServerConnected()}")

        # Define other instance attributes for later population
        self.ccd = None
        self.device_ccd = None
        self.exptime = None
        self.exptype = None
        self.ccd_binning = (1, 1)

    def handle_message(self):
        """Handle messages from the broker

        Calls all prarent-class handle_message() methods for API parsing.

        Parent classes present the API for that device type, and since this
        Agent is a composite of multiple devices, we must call all of the
        relevant message handlers.
        """
        # Search through the Method Resolution Order, skipping this class
        for parent in self.__class__.__mro__[1:]:
            if hasattr(parent, "handle_message"):
                parent.handle_message(self)

    def connect_to_cooler(self):
        """CoolerAgent: Connect to the cooler

        Connect to the cooler control.
        NOTE: This is not required for the QHY 600M outside of the camera
              connection.
        """
        if not self.check_camera_connection():
            self.connect_to_camera()

    def set_temperature(self, cool_temp, tolerance=1.0):
        """CoolerAgent: Set the cooler temperature

        Set the temperature goal of the cooler.  For the QHY600M, this also
        turns on the cooler power.

        Parameters
        ----------
        cool_temp : ``float``
            The desired cooler set point in degrees Celsius
        tolerance : ``float``
            Tolerance between CCD temperature and ``cool_temp`` before issuing
            a "Go" command to the DTO.
        """
        if not self.check_camera_connection():
            return
        print(f"QHY600 Setting Cooler Temperature to {cool_temp:.1f}ºC")

        # Get the number vector property, set the new value, and send it back
        temp = self.device_ccd.getNumber("CCD_TEMPERATURE")
        temp[0].value = float(cool_temp)  ### new temperature to reach
        self.indiclient.sendNewNumber(temp)

        # NOTE: This should probably also send a "Wait" command back to the DTO
        #       and should quietly loop until either the temperature reaches
        #       the requested value or a timeout is reached.
        self.conn.send(body="Wait", destination="/topic/" + self.config["dto_topic"])

        ccd_cooler_temp = self.camera_status["CCD_TEMPERATURE"]["vals"][0][1]
        ccd_cooler_powr = self.camera_status["CCD_COOLER_POWER"]["vals"][0][1]

        print(f"Temperature difference: {np.abs(ccd_cooler_temp - cool_temp)}  Tolerance: {tolerance}   IF conditional: {np.abs(ccd_cooler_temp - cool_temp) > tolerance}")

        while np.abs(ccd_cooler_temp - cool_temp) > tolerance:
            temp = self.device_ccd.getNumber("CCD_TEMPERATURE")
            temp[0].value = float(cool_temp)  ### new temperature to reach
            self.indiclient.sendNewNumber(temp)
            
            time.sleep(1.0)
            ccd_cooler_temp = self.camera_status["CCD_TEMPERATURE"]["vals"][0][1]
            ccd_cooler_powr = self.camera_status["CCD_COOLER_POWER"]["vals"][0][1]
            print(
                f"CCD Temp: {ccd_cooler_temp:.1f}ºC  "
                f"Set point: {cool_temp:.1f}ºC  "
                f"Cooler Power: {ccd_cooler_powr:.0f}%"
            )
        print(f"Cooler is stable at {ccd_cooler_temp:.1f}ºC, cooler power: {ccd_cooler_powr:.0f}%")
        self.conn.send(body="Go", destination="/topic/" + self.config["dto_topic"])

    def connect_to_camera(self):
        """CameraAgent: Connect to the camera

        Connect to the camera control.
        """
        # List out the devices available from the INDI server
        devlist = [d.getDeviceName() for d in self.indiclient.getDevices()]
        print(f"This is the list of connected devices: {devlist}")

        # Check that the desired CCD is in the list of devices on the INDI server
        self.ccd = self.config["camera_type"]
        if self.ccd not in devlist:
            print(f"Warning: {self.ccd} not in the list of available INDI devices!")
            return

        # Get the device from the INDI server
        device_ccd = self.indiclient.getDevice(self.ccd)
        while not device_ccd:
            print("  Waiting on connection to the CMOS Camera...")
            time.sleep(0.5)
            device_ccd = self.indiclient.getDevice(self.ccd)
        self.device_ccd = device_ccd

        # Make the connection -- exit if no connection
        ccd_connect = self.device_ccd.getSwitch("CONNECTION")
        while not ccd_connect:
            print("not connected")
            time.sleep(0.5)
            ccd_connect = self.device_ccd.getSwitch("CONNECTION")
        while not device_ccd.isConnected():
            print("still not connected")
            ccd_connect[0].s = PyIndi.ISS_ON  # the "CONNECT" switch
            ccd_connect[1].s = PyIndi.ISS_OFF  # the "DISCONNECT" switch
            self.indiclient.sendNewSwitch(ccd_connect)
            time.sleep(0.5)
        print(f"Are we connected yet? {self.device_ccd.isConnected()}")
        if not self.device_ccd.isConnected():
            sys.exit()

        # Print a happy acknowledgment
        print(f"The Agent is now connected to {self.ccd}")

        # Tell the INDI server send the "CCD1" blob to this client
        self.indiclient.setBLOBMode(PyIndi.B_ALSO, self.ccd, "CCD1")

    def status(self):
        """CameraAgent / CoolerAgent: Report the status

        _extended_summary_
        """
        if not self.check_camera_connection():
            return
        # print("QHY600 Status...")

    def set_exposure_length(self, exposure_length):
        """CameraAgent: Set the exposure length

        This is a separate command from expose(), and saves the desired
        exposure time into the instance attribute ``exptime``.

        Parameters
        ----------
        exposure_length : ``float``
            The desired exposure time in seconds.
        """
        if not self.check_camera_connection():
            return
        print("QHY600 Setting Exposure Length...")
        print(f"This is the exposure time passed from on high: {exposure_length}")
        self.exptime = exposure_length

    def set_exposure_type(self, exposure_type):
        """CameraAgent: Set the exposure type

        This is a separate command from expose(), and saves the desired
        exposure type into the instance attribute ``exptype``.

        Parameters
        ----------
        exposure_type : ``str``
            The desired exposure type.
        """
        if not self.check_camera_connection():
            return
        print("QHY600 Setting Exposure Type...")
        print(f"This is the exposure type passed from on high: {exposure_type}")
        self.exptype = exposure_type

    def set_binning(self, x_binning, y_binning):
        """CameraAgent: Set the CCD binning

        _extended_summary_

        Parameters
        ----------
        x_binning : ``int``
            CCD binning in the x direction
        y_binning : ``int``
            CCD binning in the y direction
        """
        if not self.check_camera_connection():
            return
        print("QHY600 Setting Binning...")
        print(f"This is the CCD binning passed from on high: {(x_binning, y_binning)}")
        self.ccd_binning = (x_binning, y_binning)

    def set_origin(self, x, y):
        """CameraAgent: Set the origin of a subregion

        _extended_summary_

        Parameters
        ----------
        x : _type_
            _description_
        y : _type_
            _description_
        """
        if not self.check_camera_connection():
            return
        print("QHY600 Setting Origin...")

    def set_size(self, width, height):
        """CameraAgent: Set the size of a subregion

        _extended_summary_

        Parameters
        ----------
        width : _type_
            _description_
        height : _type_
            _description_
        """
        if not self.check_camera_connection():
            return
        print("QHY600 Setting Size...")

    def expose(self, n_exp=1):
        """CameraAgent: Take an exposure

        This method takes an exposure with the camera.  The various settings
        need to have been adjusted before this command is executed.  If any of
        the required settings are ``None``, this method will emmit a warning
        and return without exposing.

        NOTE: An exposure is triggered when the exposure number vector property
              is sent to the camera via the INDI server, like::

                self.indiclient.sendNewNumber(ccd_exposure)

        Parameters
        ----------
        n_exp : ``int``
            Number of exposures to be taken.  (Default: 1)
        """
        if not self.check_camera_connection():
            return
        print("QHY600 Expose...")

        # Check the required exposure properties
        if not self.exptime:
            print("WARNING: Must specify exposure time before exposing!")
            return
        if not self.exptype:
            print("WARNING: Must specify exposure type before exposing!")
            return

        # Say what we're going to do
        print(f"Exposing {self.exptype} frame for {self.exptime:.2f}s...")

        # TODO: Need to figure out how to specify things like the exposure
        #       type, binning, and ROI to the INDI server.  Do those things
        #       here.

        # =====================================================================#
        # NOTE: For testing, we are snooping on the Telescope Simulator to
        #       provide sky coordinate information for the FITS headers. When
        #       Locutus is avaialable, this section will be replaced with code
        #       appropriate for pulling in the FITS header information from
        #       that source.
        while not (ccd_active_devices := self.device_ccd.getText("ACTIVE_DEVICES")):
            time.sleep(0.5)
        ccd_active_devices[0].text = "Telescope Simulator"
        self.indiclient.sendNewText(ccd_active_devices)
        # =====================================================================#

        # Retrieve the CCD_EXPOSURE number vector property from the camera
        while not (ccd_exposure := self.device_ccd.getNumber("CCD_EXPOSURE")):
            time.sleep(0.5)

        # Retrieve the CCD1 vector blob property from the camera
        while not (ccd_ccd1 := self.device_ccd.getBLOB("CCD1")):
            time.sleep(0.5)
            sys.stderr.write(".")
        print(f"Got BLOB CCD1 from {self.ccd}")

        # Set up the list of desired exposure time(s)
        exposures = [self.exptime for _ in range(n_exp)]

        # Set up threading so that the next exposure can begin while the
        #   present one is being processed
        self.indiclient.blobEvent.clear()

        # Set the ccd_exposure value to the first in the list and send it to
        #   the camera to begin taking the exposure.
        ccd_exposure[0].value = exposures[0]
        self.indiclient.sendNewNumber(ccd_exposure)

        # Loop through the number of exposures to be taken
        for i in range(len(exposures)):

            # Wait for the ith exposure
            self.indiclient.blobEvent.wait()

            # When it arrives, immediately start the next one
            if i + 1 < len(exposures):
                ccd_exposure[0].value = exposures[i + 1]
                self.indiclient.blobEvent.clear()
                self.indiclient.sendNewNumber(ccd_exposure)

            # Meanwhile, process the received exposure
            for blob in ccd_ccd1:
                # Print out some information about this exposure
                print(f"name: {blob.name} size: {blob.size} format: {blob.format}")

                # Use the PyIndi-supplied getblobdata() method to access the contents of
                #   the BLOB, which is a bytearray in Python.  Run it through io.BytesIO
                #   and AstroPy to produce a fully functional FITS HDUList.
                hdulist = astropy.io.fits.open(io.BytesIO(blob.getblobdata()))

                # Write to disk
                # TODO: Here is where we'd add the Locutus-supplied FITS header information
                #       Also, figure out how to do some sort of incremental file numbering
                #       or something.
                hdulist.writeto("simimage.fits", overwrite=True)

    def check_camera_connection(self):
        """Check that the client is connected to the camera

        Returns
        -------
        ``bool``
            Whether the camera is connected
        """
        if self.device_ccd and self.device_ccd.isConnected():
            return True

        print("Warning: Camera must be connected first (camera : connect_to_camera)")
        return False


# =============================================================================#
# Command line interface

if __name__ == "__main__":

    # Instantiate the Agent
    qca = QHY600Agent("qhy600_config.yaml")

    # Loop forever!
    while True:

        # If a message has been received since the last loop...
        if qca.message_received:

            qca.handle_message()
            qca.message_received = 0
            """ isca.conn.send(
                body="Wait",
                destination="/topic/" + isca.config["broadcast_topic"],
            )

            if "camera" in isca.current_message:
                isca.conn.send(
                    body="Wait",
                    destination="/topic/" + isca.config["dto_topic"],
                )
                time.sleep(2.0)
                isca.conn.send(
                    body="Go",
                    destination="/topic/" + pwma.config["dto_topic"],
                )

            # If command in wait_list, send "Wait" to DTO, check status
            # until is_slewing is false, then send "Go" to DTO.
            if any(s in isca.current_message for s in pwma.wait_list):
                # print("we are in a wait loop")
                # Send mount status back to DTO.
                isca.conn.send(
                    body="Wait",
                    destination="/topic/" + isca.config["dto_topic"],
                )
                # time.sleep(0.5)
                while True:
                    isca.get_status_and_broadcast()
                    # print("is_slewing: ", pwma.mount_status.mount.is_slewing)
                    if not isca.mount_status.mount.is_slewing:
                        break

                isca.conn.send(
                    body="Go",
                    destination="/topic/" + isca.config["dto_topic"],
                ) """
            # time.sleep(0.5)
            # time.sleep(0.1)

        # Otherwise, wait and broadcast status
        else:
            time.sleep(0.5)
            qca.get_status_and_broadcast()
