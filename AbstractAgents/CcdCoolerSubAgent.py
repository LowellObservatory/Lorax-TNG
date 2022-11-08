"""
Created on Sept. 19, 2022
@author: dlytle

"""
from abc import abstractmethod
from AbstractAgents.SubAgent import SubAgent


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

        if "init" in message:
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
