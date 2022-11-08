"""
Created on Sept. 19, 2022
@author: dlytle

"""
from abc import abstractmethod
from AbstractAgents.SubAgent import SubAgent


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

        if "init" in message:
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
