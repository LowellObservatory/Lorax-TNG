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
    status
        Broadcast the current status of the camera
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
from CommandLanguage import parse_dscl


class CameraSubAgent(SubAgent):
    """Camera SubAgent

    This SubAgent contains the methods common to all Camera instances,
    regardless of the hardware communication protocol.  Namely, the populated
    methods contained herein merely set instance attributes and do not
    communicate directly with the hardware.  Also, this class handles all of
    the camera message commands, to minimize replication between pieces of
    hardware.

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
        self.gain = None
        self.n_exposures = None
        self.img_title = None
        self.fits_comment = None
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

        # Parse out the message; check it went to the right place
        target, command, arguments = parse_dscl.parse_command(message)
        if target not in ["camera", "allserv"]:
            raise ValueError("NON-CAMERA command sent to camera!")

        # CASE out the COMMAND
        if command == "init":
            print("Connecting to the camera...")
            # Call hardware-specific method
            self.connect_to_camera()

        elif command == "disconnect":
            print("Disconnecting from camera...")
            # Reset all internal attributes
            self.ccd = None
            self.device_ccd = None
            self.exptime = None
            self.exptype = None
            self.ccd_binning = (1, 1)
            # Call hardware-specific method
            self.disconnect_from_camera()

        elif command == "status":
            # Call hardware-specific method
            self.get_status_and_broadcast()

        elif command == "expose":
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

            # Call hardware-specific method
            self.expose()

        elif command == "pause_exposure":
            # Call hardware-specific method
            self.pause_exposure()

        elif command == "resume_exposure":
            # Call hardware-specific method
            self.resume_exposure()

        elif command == "abort":
            # Call hardware-specific method
            self.abort_exposure()

        elif command == "set_exposure_length":
            # There should be ONE argument, and it should be a float
            if len(arguments) != 1 or not isinstance(arguments[0], float):
                warnings.warn("Exposure time must be a single float value.")
                return
            exptime = arguments[0]

            # Check arguments against exposure length limits.

            # Set the instance attribute
            self.exptime = exptime
            print(f"Exposure length set to {exptime:.2f}s")

        elif command == "set_num_exposures":
            # There should be ONE argument, and it should be a float
            if len(arguments) != 1 or not isinstance(arguments[0], float):
                warnings.warn("Number of exposures must be a single number.")
                return
            n_exposures = int(arguments[0])

            # Check arguments against number of exposure limits.

            # Set the instance attribute
            self.n_exposures = n_exposures
            print(f"Number of exposures set to {n_exposures}")

        elif command == "set_exposure_type":
            # There should be ONE argument, and it should be a string
            if len(arguments) != 1 or not isinstance(arguments[0], str):
                warnings.warn("Exposure type must be a single string.")
                return
            exptype = arguments[0]

            # Check arguments against exposure types.

            # Set the instance attribute
            self.exptype = exptype
            print(f"Exposure type set to {exptype}")

        elif command == "set_binning":
            # check arguments against binning limits.
            # send camera specific set_binning.
            print("camera: set_binning (no effect)")

        elif command == "set_origin":
            # check arguments against origin limits.
            # send camera specific set_origin.
            print("camera: set_origin (no effect)")

        elif command == "set_size":
            # check arguments against size limits.
            # send camera specific set_size.
            print("camera: set_size (no effect)")

        elif command == "set_gain":
            # There should be ONE argument, and it should be a float
            if len(arguments) != 1 or not isinstance(arguments[0], float):
                warnings.warn("Gain must be a single float value.")
                return
            gain = arguments[0]

            # Check arguments against exposure length limits.

            # Set the instance attribute
            self.gain = gain
            print(f"Gain set to {gain:.2f}s")

        elif command == "set_image_title":
            # There should be ONE argument, and it should be a string
            if len(arguments) != 1 or not isinstance(arguments[0], str):
                warnings.warn("Image title must be a single string.")
                return
            img_title = arguments[0]

            # Set the instance attribute
            self.img_title = img_title
            print(f"Image title set to {img_title}")

        elif command == "set_fits_comment":
            # There should be ONE argument, and it should be a string
            if len(arguments) != 1 or not isinstance(arguments[0], str):
                warnings.warn("FITS comment must be a single string.")
                return
            fits_comment = arguments[0]

            # Set the instance attribute
            self.fits_comment = fits_comment
            print(f"FITS comment set to {img_title}")

        elif command == "set_image_directory":
            print("camera: set_image_directory (no effect)")

        elif command == "reset_frame":
            print("camera: reset_frame (no effect)")

        elif command == "reset_properties":
            print("camera: reset_properties (no effect)")

        else:
            warnings.warn(f"Unknown command: {command}")

    def check_camera_connection(self):
        """Check that the client is connected to the camera

        Returns
        -------
        ``bool``
            Whether the camera is connected
        """
        if self.device_ccd and self.device_ccd.isConnected():
            return True

        print("Warning: Camera must be connected first (camera: connect_to_camera)")
        return False

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

    @abstractmethod
    def disconnect_from_camera(self):
        """Disconnect from camera

        Must be implemented by hardware-specific Agent
        """

    @abstractmethod
    def expose(self):
        """Take an exposure

        Must be implemented by hardware-specific Agent
        """

    @abstractmethod
    def pause_exposure(self):
        """Pause an in-progress exposure

        Must be implemented by hardware-specific Agent
        """

    @abstractmethod
    def resume_exposure(self):
        """Resume a paused exposure

        Must be implemented by hardware-specific Agent
        """

    @abstractmethod
    def abort_exposure(self):
        """Abort an in-progress or paused exposure

        Must be implemented by hardware-specific Agent
        """
