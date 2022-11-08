# -*- coding: utf-8 -*-
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
#  Created on 08-Nov-2022
#
#  @author: dlytle, tbowers

"""Lorax Camera SubAgent Abstract Class

This module is part of the Lorax-TNG package, written at Lowell Observatory.

This SubAgent is to be inherited by all protocol-based Camera Agents, and
provides the complete API for all Lorax Camera Agents (contained in the
:func:`handle_message` method).

The Lorax Camera API is as follows:
===================================

    init
        Initialize and connect to the camera
    disconnect
        Disconnect from the camera
    expose
        Take an exposure with the currently defined settings
    pause_exposure
        Pause the exposure without reading out the detector
    resume_exposure
        Resume a previously paused exposure
    abort
        Abort the exposure completely (exposure lost)
    set_exposure_length
        Set the exposure length
    set_num_exposures
        Set the number of exposures to take
    set_exposure_type
        Set the exposure type
    set_binning
        Set the binning of the detector
    set_origin
        Set the origin for a subframe
    set_size
        Set the size for a subframe
    set_gain
        Set the gain of the detector
    set_image_title
        Set the image title to be placed in the FITS header
    set_fits_comment
        Set the FITS comment field to be included in the header
    set_image_directory
        Set the directory into which the FITS images will be stored
    reset_frame
        Reset the binning, origin, and size properties to initial values
    reset_properties
        Reset all of the ``set_*`` properties to initial values

"""

# Built-In Libraries
from abc import abstractmethod
import warnings

# 3rd Party Libraries

# Internal Imports
from AbstractAgents.SubAgent import SubAgent


class CameraSubAgent(SubAgent):
    """Camera SubAgent

    This SubAgent contains the methods common to all Camera instances,
    regardless of the hardware communication protocol.  Namely, the populated
    methods contained herein merely set instance attributes and do not
    communicate directly with the hardware.  Also, this class handles all of
    the camera message commands, to minimize replication between pieces of hardware.

    Abstract methods are supplied for the functions expected to have hardware-
    specific implementation needs.

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
        super().__init__(logger, conn, config)

        # Define other instance attributes for later population

        self.ccd = None
        self.device_ccd = None
        self.exptime = None
        self.exptype = None
        self.ccd_binning = (1, 1)

    def handle_message(self, message):
        """Handle an incoming message

        This method contains the API for the CameraSubAgent.  Incoming messages
        are compared against the command list, and the proper method is called.
        Some of the API commands are general to all Camera Agents and are fully
        implemented here; others are hardware-specific and are left as abstract
        methods for later implementation.

        Parameters
        ----------
        message : str
            The incoming message from the broker, as passed down from the
            Composite Agent.
        """
        print(f"\nReceived message in CameraSubAgent: {message}")

        if "init" in message:
            print("Connecting to the camera...")
            self.connect_to_camera()

        elif "disconnect" in message:
            print("Disconnecting from camera...")
            # Reset all internal attributes
            self.ccd = None
            self.device_ccd = None
            self.exptime = None
            self.exptype = None
            self.ccd_binning = (1, 1)

        elif "expose" in message:
            # check arguments.
            # check exposure settings.
            # send "wait" to DTO.
            # request FITS dictionary from Locutus.
            # send camera specific command to camera. (call cam_specific_expose)
            # when done, request another FITS dictionary from Locutus.
            # save image data to local disk.
            # spawn fits_writer in seperate process (data, fits1, fits2)
            # send "go" command to DTO.
            # print("camera:take exposure")
            self.expose()

        elif "pause_exposure" in message:
            print("camera:pause_exposure (no effect)")

        elif "resume_exposure" in message:
            print("camera:resume_exposure (no effect)")

        elif "abort" in message:
            print("camera:abort (no effect)")

        elif "set_exposure_length" in message:
            # check arguments against exposure length limits.
            # send camera specific set_exposure_length.
            # print("camera:set_exposure_length")
            try:
                exptime = float(message[message.find("(") + 1 : message.find(")")])
            except ValueError:
                print("Exposure time must be a float.")
                return
            self.set_exposure_length(exptime)
            print(f"Exposure length set to {exptime:.2f}s")

        elif "set_num_exposures" in message:
            print("camera:set_num_exposures (no effect)")

        elif "set_exposure_type" in message:
            # check arguments against exposure types.
            # send camera specific set_exposure_type.
            # print("camera:set_exposure_type")
            try:
                exptype = str(message[message.find("(") + 1 : message.find(")")])
            except ValueError:
                print("Exposure type must be a str.")
                return
            self.set_exposure_type(exptype)
            print(f"Exposure type set to {exptype}")

        elif "set_binning" in message:
            # check arguments against binning limits.
            # send camera specific set_binning.
            print("camera:set_binning (no effect)")

        elif "set_origin" in message:
            # check arguments against origin limits.
            # send camera specific set_origin.
            print("camera:set_origin (no effect)")

        elif "set_size" in message:
            # check arguments against size limits.
            # send camera specific set_size.
            print("camera:set_size (no effect)")

        elif "set_gain" in message:
            # check arguments against gain limits.
            # send camera specific set_gain.
            print("camera:set_size (no effect)")

        elif "set_image_title" in message:
            print("camera:set_image_title (no effect)")

        elif "set_fits_comment" in message:
            print("camera:set_fits_comment (no effect)")

        elif "set_image_directory" in message:
            print("camera:set_image_directory (no effect)")

        elif "reset_frame" in message:
            print("camera:reset_frame (no effect)")

        elif "reset_properties" in message:
            print("camera:reset_properties (no effect)")

        else:
            warnings.warn("Unknown command")

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

    def set_exposure_length(self, exposure_length):
        """Set the exposure length

        This is a separate command from expose(), and saves the desired
        exposure time into the instance attribute ``exptime``.

        Parameters
        ----------
        exposure_length : ``float``
            The desired exposure time in seconds.
        """
        if not self.check_camera_connection():
            return
        print(f"CameraSubAgent Setting Exposure Length to {exposure_length}s")
        self.exptime = exposure_length

    def set_exposure_type(self, exposure_type):
        """Set the exposure type

        This is a separate command from expose(), and saves the desired
        exposure type into the instance attribute ``exptype``.

        Parameters
        ----------
        exposure_type : ``str``
            The desired exposure type.
        """
        if not self.check_camera_connection():
            return
        print(f"CameraSubAgent Setting Exposure Type to {exposure_type}")
        self.exptype = exposure_type

    def set_binning(self, x_binning, y_binning):
        """Set the CCD binning

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
        print(f"CameraSubAgent Setting Binning to {(x_binning, y_binning)}")
        self.ccd_binning = (x_binning, y_binning)

    def set_origin(self, x, y):
        """Set the origin of a subregion

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
        print("CameraSubAgent Setting Origin (not really)")

    def set_size(self, width, height):
        """Set the size of a subregion

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
        print("CameraSubAgent Setting Size (not really)")

    @abstractmethod
    def connect_to_camera(self):
        """Connect to camera

        Must be implemented by hardware-specific Agent
        """
        raise NotImplementedError("Specific hardware Agent must implement this method.")

    @abstractmethod
    def expose(self):
        """Take an exposure

        Must be implemented by hardware-specific Agent
        """
        raise NotImplementedError("Specific hardware Agent must implement this method.")
