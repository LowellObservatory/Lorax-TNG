"""
Created on Sept. 19, 2022
@author: dlytle

"""
from abc import ABC, abstractmethod

# General Sub-Agent class, inherit from Abstract Base Class
class SubAgent(ABC):
    """SubAgent

    _extended_summary_
    """

    def __init__(self, logger, conn, config):
        # print(config)
        self.logger = logger
        self.conn = conn
        self.config = config

    @abstractmethod
    def get_status_and_broadcast(self):
        """Get hardware status and broadcast on the broker

        Must be implemented by inheriting class.
        """

    @abstractmethod
    def handle_message(self, message):
        """Handle incoming messages from the broker

        Must be implemented by inheriting class.
        """


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

        if "connect_to_camera" in message:
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


class CcdCoolerSubAgent(SubAgent):
    """CCD Cooler SubAgent

    This SubAgent contains the methods common to all CCD COOLER instances,
    regardless of the hardware communication protocol.  Namely, the populated
    methods contained herein merely set instance attributes and do not
    communicate directly with the hardware.  Also, this class handles all of
    the cooler message commands, to minimize replication between pieces of hardware.

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
        self.cooler = None
        self.device_cooler = None

    def handle_message(self, message):
        print(f"\nReceived message in CcdCoolerSubAgent: {message}")

        if "connect_to_cooler" in message:
            print("Connecting to the cooler...")
            self.connect_to_cooler()

        elif "disconnect" in message:
            print("Disconnecting from cooler...")
            self.disconnect_from_cooler()
            self.cooler = None
            self.device_cooler = None

        elif "set_temperature" in message:
            # Get the arguments.
            # setTemp(-45.0)
            # print("doing settemp")
            com = message
            temperature = float(com[com.find("(") + 1 : com.find(")")])
            self.set_temperature(temperature)
            print(f"Temperature set to {temperature:.1f}ºC")

        elif "status" in message:
            # print("doing status")
            self.get_status_and_broadcast()

        # if "set_temp" in message:
        # send set temp.
        # send "wait" to DTO.
        # send specific command, "set temp", to ccd cooler
        # keep checking status until temp within limits.
        # send "go" command to DTO.
        # print("ccd cooler: set temp")
        # if "report_temp" in message:
        # report temp.
        # send specific command, "report temp", to ccd cooler
        # broadcast temp
        # print("ccd cooler: report temp")

        else:
            print("Unknown command")

    def check_cooler_connection(self):
        """Check that the client is connected to the CCD cooler

        Returns
        -------
        ``bool``
            Whether the CCD cooler is connected
        """
        if self.device_cooler and self.device_cooler.isConnected():
            return True

        print(
            "Warning: CCD Cooler must be connected first (cooler : connect_to_cooler)"
        )
        return False

    @abstractmethod
    def connect_to_cooler(self):
        """Connect to CCD cooler

        Must be implemented by hardware-specific Agent
        """
        raise NotImplementedError("Specific hardware Agent must implement this method.")

    @abstractmethod
    def disconnect_from_cooler(self):
        """Disconnect from CCD cooler

        Must be implemented by hardware-specific Agent
        """
        raise NotImplementedError("Specific hardware Agent must implement this method.")

    @abstractmethod
    def set_temperature(self, cool_temp):
        """Set the CCD cooler temperature

        Must be implemented by hardware-specific Agent
        """
        raise NotImplementedError("Specific hardware Agent must implement this method.")


class FilterWheelSubAgent(SubAgent):
    """Filter Wheel SubAgent

    This SubAgent contains the methods common to all FILTER WHEEL instances,
    regardless of the hardware communication protocol.  Namely, the populated
    methods contained herein merely set instance attributes and do not
    communicate directly with the hardware.  Also, this class handles all of
    the cooler message commands, to minimize replication between pieces of hardware.

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
        self.filterwheel = None
        self.device_filterwheel = None

    def handle_message(self, message):
        print(f"\nReceived message in FilterWheelSubAgent: {message}")

        if "connect_to_filterwheel" in message:
            print("Connecting to the filter wheel...")
            self.connect_to_filterwheel()

        elif "disconnect" in message:
            print("Disconnecting from filter wheel...")
            self.disconnect_from_filterwheel()

        elif "home" in message:
            # send wheel home.
            # send "wait" to DTO.
            # send specific command, "home", to filter wheel
            # keep checking status until done.
            # send "go" command to DTO.
            print("filter wheel: home")

        elif "move" in message:
            # send wheel to specific position.
            # check arguments against position limits.
            # send "wait" to DTO.
            # send specific command, "movoto x", to filter wheel
            # keep checking status until done.
            # send "go" command to DTO.
            print("filter wheel: move")

        else:
            print("Unknown command")

    def check_filterwheel_connection(self):
        """Check that the client is connected to the filter wheel

        Returns
        -------
        ``bool``
            Whether the filter wheel is connected
        """
        if self.device_filterwheel and self.device_filterwheel.isConnected():
            return True

        print(
            "Warning: Filter Wheel must be connected first (filterwheel : connect_to_filterwheel)"
        )
        return False

    @abstractmethod
    def connect_to_filterwheel(self):
        """Connect to filter wheel

        Must be implemented by hardware-specific Agent
        """
        raise NotImplementedError("Specific hardware Agent must implement this method.")

    @abstractmethod
    def disconnect_from_filterwheel(self):
        """Disconnect from filter wheel

        Must be implemented by hardware-specific Agent
        """
        raise NotImplementedError("Specific hardware Agent must implement this method.")

    @abstractmethod
    def move(self, slot):
        """Move the filter wheel

        Must be implemented by hardware-specific Agent
        """
        raise NotImplementedError("Specific hardware Agent must implement this method.")

    @abstractmethod
    def home(self):
        """Home the filter wheel

        Must be implemented by hardware-specific Agent
        """
        raise NotImplementedError("Specific hardware Agent must implement this method.")


class MountSubAgent(SubAgent):
    """Mount SubAgent

    This SubAgent contains the methods common to all MOUNT instances,
    regardless of the hardware communication protocol.  Namely, the populated
    methods contained herein merely set instance attributes and do not
    communicate directly with the hardware.  Also, this class handles all of
    the cooler message commands, to minimize replication between pieces of hardware.

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
        self.mount = None
        self.device_mount = None

    def handle_message(self, message):
        print(f"\nReceived message in MountSubAgent: {message}")

        if "connect_to_mount" in message:
            print("Connecting to the mount...")
            self.connect_to_mount()

        elif "disconnect" in message:
            print("Disconnecting from mount...")
            self.disconnect_from_mount()

        elif "home" in message:
            # send mount home.
            # send "wait" to DTO.
            # send specific command, "home", to filter wheel
            # keep checking status until done.
            # send "go" command to DTO.
            print("mount: home")

        elif "move" in message:
            # send mount to specific position.
            # check arguments against position limits.
            # send "wait" to DTO.
            # send specific command, "movoto x", to filter wheel
            # keep checking status until done.
            # send "go" command to DTO.
            print("mount: move")

        else:
            print("Unknown command")

    def check_mount_connection(self):
        """Check that the client is connected to the mount
        Returns
        -------
        ``bool``
            Whether the mount is connected
        """
        if self.device_mount and self.device_mount.isConnected():
            return True

        print("Warning: Mount must be connected first (mount : connect_to_mount)")
        return False

    @abstractmethod
    def connect_to_mount(self):
        """Connect to mount

        Must be implemented by hardware-specific Agent
        """
        raise NotImplementedError("Specific hardware Agent must implement this method.")

    @abstractmethod
    def disconnect_from_mount(self):
        """Disconnect from mount

        Must be implemented by hardware-specific Agent
        """
        raise NotImplementedError("Specific hardware Agent must implement this method.")

    @abstractmethod
    def move(self, slot):
        """Move the mount

        Must be implemented by hardware-specific Agent
        """
        raise NotImplementedError("Specific hardware Agent must implement this method.")

    @abstractmethod
    def home(self):
        """Home the mount

        Must be implemented by hardware-specific Agent
        """
        raise NotImplementedError("Specific hardware Agent must implement this method.")


class DomeSubAgent(SubAgent):
    """Dome SubAgent

    This SubAgent contains the methods common to all DOME instances,
    regardless of the hardware communication protocol.  Namely, the populated
    methods contained herein merely set instance attributes and do not
    communicate directly with the hardware.  Also, this class handles all of
    the cooler message commands, to minimize replication between pieces of hardware.

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
        self.dome = None
        self.device_dome = None

    def handle_message(self, message):
        print(f"\nReceived message in DomeSubAgent: {message}")

        if "connect_to_dome" in message:
            print("Connecting to the dome...")
            self.connect_to_dome()

        elif "disconnect" in message:
            print("Disconnecting from dome...")
            self.disconnect_from_dome()

        elif "home" in message:
            # send dome home.
            # send "wait" to DTO.
            # send specific command, "home", to filter wheel
            # keep checking status until done.
            # send "go" command to DTO.
            print("dome: home")

        elif "move" in message:
            # send dome to specific position.
            # check arguments against position limits.
            # send "wait" to DTO.
            # send specific command, "movoto x", to filter wheel
            # keep checking status until done.
            # send "go" command to DTO.
            print("dome: move")

        else:
            print("Unknown command")

    def check_dome_connection(self):
        """Check that the client is connected to the dome
        Returns
        -------
        ``bool``
            Whether the dome is connected
        """
        if self.device_dome and self.device_dome.isConnected():
            return True

        print("Warning: Dome must be connected first (dome : connect_to_dome)")
        return False

    @abstractmethod
    def connect_to_dome(self):
        """Connect to dome

        Must be implemented by hardware-specific Agent
        """
        raise NotImplementedError("Specific hardware Agent must implement this method.")

    @abstractmethod
    def disconnect_from_dome(self):
        """Disconnect from dome

        Must be implemented by hardware-specific Agent
        """
        raise NotImplementedError("Specific hardware Agent must implement this method.")

    @abstractmethod
    def move(self, slot):
        """Move the dome

        Must be implemented by hardware-specific Agent
        """
        raise NotImplementedError("Specific hardware Agent must implement this method.")

    @abstractmethod
    def home(self):
        """Home the dome

        Must be implemented by hardware-specific Agent
        """
        raise NotImplementedError("Specific hardware Agent must implement this method.")
