"""
Created on Sept. 19, 2022
@author: dlytle

"""
from abc import abstractmethod
from AbstractAgents.SubAgent import SubAgent


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

        if "init" in message:
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