"""
Created on Sept. 19, 2022
@author: dlytle

"""
from abc import abstractmethod
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

        else:
            print("Unknown command")

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
