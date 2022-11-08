"""
Created on Sept. 19, 2022
@author: dlytle

"""
from abc import abstractmethod
from AbstractAgents.SubAgent import SubAgent


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

        if "init" in message:
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
