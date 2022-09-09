# -*- coding: utf-8 -*-
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
#  Created on 21-Oct-2022
#
#  @author: dlytle, tbowers

"""Lorax Camera Agent for the QHY 600M CMOS Camera

This module is part of the Lorax-TNG package, written at Lowell Observatory.

This Camera Agent concerns itself with the camera aspects of the QHY600M, and
its functionality is called from the QHY600Composite module.

Hardware control of the QHY 600M is accomplished through an INDI interface,
contained in the HardwareClients module.
"""

# Built-In Libraries
import io
import sys
import time

# 3rd Party Libraries
import astropy.io.fits
import PyIndi

# Internal Imports
from HardwareClients import IndiClient
from SubAgent import SubAgent


class QHY600Camera(SubAgent):
    """QHY600M Camera Agent (SubAgent to QHY600Composite)

    _extended_summary_

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
        print("in QHY600Camera.init")
        SubAgent.__init__(self, logger, conn, config)

        # -----
        # Get the host and port for the connection to mount.
        # "config", in this case, is just a dictionary.
        self.indiclient = IndiClient(self)
        # print(self.config)
        self.indiclient.setServer(
            self.config["camera_host"], self.config["camera_port"]
        )
        self.device_status = {}

        self.indiclient.connectServer()

        device_ccd = self.indiclient.getDevice(self.config["camera_name"])
        while not device_ccd:
            time.sleep(0.5)
            device_ccd = self.indiclient.getDevice(self.config["camera_name"])

        self.device_ccd = device_ccd
        print(self.device_ccd)
        # -----

        # Define other instance attributes for later population
        self.ccd = None
        self.exptime = None
        self.exptype = None
        self.ccd_binning = (1, 1)

    def get_status_and_broadcast(self):
        # current_status = self.status()
        # print("Status: " + current_status)
        print("camera status")

    def handle_message(self, message):
        print("got message: in QHY600Camera")
        print(message)
        if "connect_to_camera" in message:
            print("doing connect_to_camera")
            self.connect_to_camera()

        if "expose" in message:
            # check arguments.
            # check exposure settings.
            # send "wait" to DTO.
            # request FITS dictionary from Locutus.
            # send camera specific command to camera. (call cam_specific_expose)
            # when done, request another FITS dictionary from Locutus.
            # save image data to local disk.
            # spawn fits_writer in seperate process (data, fits1, fits2)
            # send "go" command to DTO.
            print("camera:take exposure")
            self.expose()
        if "set_exposure_length" in message:
            # check arguments against exposure length limits.
            # send camera specific set_exposure_length.
            print("camera:set_exposure_length")
            try:
                exptime = float(message[message.find("(") + 1 : message.find(")")])
            except ValueError:
                print("Exposure time must be a float.")
                return
            self.set_exposure_length(exptime)

        if "set_exposure_type" in message:
            # check arguments against exposure types.
            # send camera specific set_exposure_type.
            print("camera:set_exposure_type")
            try:
                exptype = str(message[message.find("(") + 1 : message.find(")")])
            except ValueError:
                print("Exposure type must be a str.")
                return
            self.set_exposure_type(exptype)

        if "set_binning" in message:
            # check arguments against binning limits.
            # send camera specific set_binning.
            print("camera:set_binning")
        if "set_origin" in message:
            # check arguments against origin limits.
            # send camera specific set_origin.
            print("camera:set_origin")
        if "set_size" in message:
            # check arguments against size limits.
            # send camera specific set_size.
            print("camera:set_size")

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
