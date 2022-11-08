# -*- coding: utf-8 -*-
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
#  Created on 21-Oct-2022
#
#  @author: dlytle, tbowers

"""Lorax Camera Agent for INDI-based CCD and CMOS cameras

This module is part of the Lorax-TNG package, written at Lowell Observatory.

This Camera Agent concerns itself with the camera aspects only of the INDI
device.  This agent is called from the CompositeAgent class by instruction from
the instrument-specific configuration file.

Hardware control of the camera is accomplished through an INDI interface,
contained in the IndiClient module.

The likely needed INDI API components for Lorax are:
    CCD_EXPOSURE - take an exposure
    CCD_ABORT_EXPOSURE - stop the exposure
    CCD_FRAME - set lower left corner and width / height of frame
    CCD_FRAME_RESET - set frame back to whole CCD, set binning to 1x1
    CCD_BINNING - set vertical and horizontal binning values
    CCD_FRAME_TYPE - set light, bias, dark, flat
    CCD_INFO - sends back size, pixel_size, bits_per_pixel of the CCD
    CCD_GAIN - may need this
    CCD_OFFSET - again, may need this
    CCD_DIRECTORY_LOCATION - where to dump the FITS files
    CCD_DIRECTORY_TOGGLE - on or off
"""

# Built-In Libraries
import datetime
import io
import sys
import time
import uuid

# 3rd Party Libraries
import astropy.io.fits
import PyIndi
import xmltodict

# Internal Imports
from AbstractAgents import CameraSubAgent
from IndiAgents.IndiClient import IndiClient


class IndiCamera(CameraSubAgent):
    """INDI Camera Agent (SubAgent to CompositeAgent)

    This class handles all of the hardware-specific portions of the CameraAgent
    implementation, leaving the more general, generic methods for the abstract
    parent class.

    Parameters
    ----------
    logger : _type_
        _description_
    conn : _type_
        _description_
    config : _type_
        _description_
    """

    def __init__(self, logger, conn, config):
        print(
            f"   ---> Initializing the INDI Camera SubAgent for {config['camera_name']}"
        )
        super().__init__(logger, conn, config)

        # Get the host and port for the connection to camera.
        # "config", in this case, is just a dictionary.
        self.indiclient = IndiClient(self, config)
        # print(self.config)
        self.indiclient.setServer(
            self.config["camera_host"], self.config["camera_port"]
        )
        self.device_status = {}

        self.indiclient.connectServer()

        # Make the connection to the specified device
        device_ccd = self.indiclient.getDevice(self.config["camera_name"])
        while not device_ccd:
            time.sleep(0.5)
            device_ccd = self.indiclient.getDevice(self.config["camera_name"])

        self.device_ccd = device_ccd

        ##### The following is from SBIGCamera.py::
        # print(self.device_ccd)
        # self.exptime = 1.0
        # self.exptype = "FRAME_LIGHT"
        # self.ccd_binning = (1, 1)

        # # List out the devices available from the INDI server
        # devlist = [d.getDeviceName() for d in self.indiclient.getDevices()]
        # print(f"This is the list of connected devices: {devlist}")

        # # Check that the desired CCD is in the list of devices on the INDI server
        # self.ccd = self.config["camera_name"]
        # if self.ccd not in devlist:
        #     print(f"Warning: {self.ccd} not in the list of available INDI devices!")
        #     return

        # # Get the device from the INDI server
        # device_ccd = self.indiclient.getDevice(self.ccd)
        # while not device_ccd:
        #     print("  Waiting on connection to the CCD Camera...")
        #     time.sleep(0.5)
        #     device_ccd = self.indiclient.getDevice(self.ccd)
        # self.device_ccd = device_ccd

        # # This is a special property of the CCD_Simulator.
        # # the CCD_Simulator requires an RA and DEC before it
        # # will take an image.  One way to do this is load
        # # the telescope simulator and connect to it.
        # # The other way is to set this property in the
        # # CCD simulator.  We do that here.
        # eqpe = device_ccd.getNumber("EQUATORIAL_PE")
        # while not eqpe:
        #     print("  Waiting for EQ_PE...")
        #     time.sleep(0.5)
        #     eqpe = device_ccd.getNumber("EQUATORIAL_PE")

        # eqpe[0].value = 0.0
        # eqpe[1].value = 0.0
        # self.indiclient.sendNewNumber(eqpe)

        # # Make the connection -- exit if no connection
        # ccd_connect = self.device_ccd.getSwitch("CONNECTION")
        # while not ccd_connect:
        #     print("not connected")
        #     time.sleep(0.5)
        #     ccd_connect = self.device_ccd.getSwitch("CONNECTION")
        # while not device_ccd.isConnected():
        #     print("still not connected")
        #     ccd_connect[0].s = PyIndi.ISS_ON  # the "CONNECT" switch
        #     ccd_connect[1].s = PyIndi.ISS_OFF  # the "DISCONNECT" switch
        #     self.indiclient.sendNewSwitch(ccd_connect)
        #     time.sleep(0.5)
        # print(f"Are we connected yet? {self.device_ccd.isConnected()}")
        # if not self.device_ccd.isConnected():
        #     pass

        # # Print a happy acknowledgment
        # print(f"The Agent is now connected to {self.ccd}")

        # # Tell the INDI server send the "CCD1" blob to this client
        # self.indiclient.setBLOBMode(PyIndi.B_ALSO, self.ccd, "CCD1")

    def get_status_and_broadcast(self):
        """Get the current status and broadcast it

        _extended_summary_
        """
        # Check if the cooler is connected
        print(
            f" &&&&&&&& Should we even be asking after the status? {self.device_ccd.isConnected()}"
        )
        device_status = self.device_status if self.device_ccd.isConnected() else {}

        c_status = {
            "message_id": uuid.uuid4(),
            "timestamput": datetime.datetime.utcnow(),
            "root": device_status,
        }
        for key in self.device_status:
            c_status[key] = self.device_status[key]
        status = {"camera": c_status}
        xml_format = xmltodict.unparse(status, pretty=True)

        # print("/topic/" + self.config["outgoing_topic"])

        self.conn.send(
            body=xml_format,
            destination="/topic/" + self.config["outgoing_topic"],
        )

    def connect_to_camera(self):
        """CameraAgent: Connect to the camera

        Connect to the camera control.
        """
        # List out the devices available from the INDI server
        devlist = [d.getDeviceName() for d in self.indiclient.getDevices()]
        print(f"This is the list of connected devices: {devlist}")

        # Check that the desired CCD is in the list of devices on the INDI server
        self.ccd = self.config["camera_name"]
        if self.ccd not in devlist:
            print(f"Warning: {self.ccd} not in the list of available INDI devices!")
            return

        # Get the device from the INDI server
        device_ccd = self.indiclient.getDevice(self.ccd)
        while not device_ccd:
            print("  Waiting on connection to the camera...")
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
        # print(f"Are we connected yet? {self.device_ccd.isConnected()}")
        if not self.device_ccd.isConnected():
            sys.exit()

        # Print a happy acknowledgment
        print(f"The Agent is now connected to {self.ccd}")

        # Tell the INDI server send the "CCD1" blob to this client
        self.indiclient.setBLOBMode(PyIndi.B_ALSO, self.ccd, "CCD1")

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
        print("IndiCamera Expose...")

        # Check the required exposure properties
        if not self.exptime:
            print("WARNING: Must specify exposure time before exposing!")
            return
        if not self.exptype:
            print("WARNING: Must specify exposure type before exposing!")
            return

        # Say what we're going to do
        print(f"Exposing {self.exptype} frame for {self.exptime:.2f}s...")

        # Send the DTO a "WAIT" message
        print(
            f"   +++> Sending 'WAIT' to {'/topic/' + self.config['dto_command_topic']}"
        )

        self.conn.send(
            body="WAIT",
            destination="/topic/" + self.config["dto_command_topic"],
        )

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
                print(
                    f"BLOB name: {blob.name}  "
                    f"size: {blob.size/1024**2:.2f} MB  "
                    f"format: {blob.format}"
                )

                # Use the PyIndi-supplied getblobdata() method to access the contents of
                #   the BLOB, which is a bytearray in Python.  Run it through io.BytesIO
                #   and AstroPy to produce a fully functional FITS HDUList.
                hdulist = astropy.io.fits.open(io.BytesIO(blob.getblobdata()))

                # Write to disk
                # TODO: Here is where we'd add the Locutus-supplied FITS header information
                #       Also, figure out how to do some sort of incremental file numbering
                #       or something.
                hdulist.writeto("simimage.fits", overwrite=True)

        # Send the DTO a "GO" message
        self.conn.send(
            body="GO",
            destination="/topic/" + self.config["dto_command_topic"],
        )
