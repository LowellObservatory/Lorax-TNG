# -*- coding: utf-8 -*-
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
#  Created on 08-Nov-2022
#
#  @author: dlytle, tbowers

"""Lorax CCD Cooler SubAgent Abstract Class

This module is part of the Lorax-TNG package, written at Lowell Observatory.

This SubAgent is to be inherited by all protocol-based CcdCooler Agents, and
provides the complete API for all Lorax CcdCooler Agents (contained in the
:func:`handle_message` method).

The Lorax CCD Cooler API is as follows:
=======================================

    init
        Initialize and connect to the cooler
    disconnect
        Disconnect from the cooler
    status
        Broadcast the current status of the cooler
    set_temperature
        Set the temperature goal for the cooler
    set_temp_tolerance
        Set the temperature stability tolerance for the cooler
    power_off
        Turn the power to the cooler off (but don't disconnect)
    power_on
        Turn the power to the cooler on, set nominal temperature

"""

# Built-In Libraries
from abc import abstractmethod
import warnings

# 3rd Party Libraries

# Internal Imports
from AbstractAgents.SubAgent import SubAgent
from CommandLanguage import parse_dscl


class CcdCoolerSubAgent(SubAgent):
    """CCD Cooler SubAgent

    This SubAgent contains the methods common to all CCD COOLER instances,
    regardless of the hardware communication protocol.  Namely, the populated
    methods contained herein merely set instance attributes and do not
    communicate directly with the hardware.  Also, this class handles all of
    the cooler message commands, to minimize replication between pieces of
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
        self.cooler = None
        self.device_cooler = None

    def handle_message(self, message):
        """Handle an incoming message

        This method contains the API for the CcdCoolerSubAgent.  Incoming
        messages are compared against the command list, and the proper method
        is called.  Some of the API commands are general to all CCD Cooler
        Agents and are fully implemented here; others are hardware-specific and
        are left as abstract methods for later implementation.

        Parameters
        ----------
        message : str
            The incoming message from the broker, as passed down from the
            Composite Agent.
        """
        print(f"\nReceived message in CcdCoolerSubAgent: {message}")

        # Parse out the message
        command, arguments = parse_dscl.parse_command(message)

        # CASE out the COMMAND
        if command == "init":
            print("Connecting to the cooler...")
            # Call hardware-specific method
            self.connect_to_cooler()

        elif command == "disconnect":
            print("Disconnecting from cooler...")
            # Call hardware-specific method
            self.disconnect_from_cooler()
            self.cooler = None
            self.device_cooler = None

        elif command == "status":
            # Call hardware-specific method
            self.get_status_and_broadcast()

        elif command == "set_temperature":
            # There should be ONE argument, and it should be a float
            if len(arguments) != 1 or not isinstance(arguments[0], float):
                warnings.warn("Set temperature must be a single float value.")
                return
            temperature = arguments[0]

            # Check arguments against temperature limits.

            # Call hardware-specific method
            self.set_temperature(temperature)
            print(f"Temperature set to {temperature:.1f}??C")

        elif command == "set_temp_tolerance":
            print("cooler: set_temp_tolerance (no effect)")

        elif command == "power_off":
            # Call hardware-specific method
            self.power_off()

        elif command == "power_on":
            print("cooler: power_on (no effect)")

        else:
            warnings.warn(f"Unknown command: {command}")

    def get_status_and_broadcast(self):
        """Get the current cooler status and broadcast it

        _extended_summary_
        """
        # Check if the cooler is connected; get status or set empty dictionary
        device_status = self.device_status if self.check_cooler_connection() else {}
        # Broadcast
        self.broadcast_status(device_status)

    def check_cooler_connection(self):
        """Check that the client is connected to the CCD cooler

        Returns
        -------
        ``bool``
            Whether the CCD cooler is connected
        """
        if self.device_cooler and self.device_cooler.isConnected():
            return True

        # print(
        #     "Warning: CCD Cooler must be connected first (cooler : connect_to_cooler)"
        # )
        return False

    @abstractmethod
    def connect_to_cooler(self):
        """Connect to CCD cooler

        Must be implemented by hardware-specific Agent
        """

    @abstractmethod
    def disconnect_from_cooler(self):
        """Disconnect from CCD cooler

        Must be implemented by hardware-specific Agent
        """

    @abstractmethod
    def set_temperature(self, cool_temp):
        """Set the CCD cooler temperature

        Must be implemented by hardware-specific Agent

        Should have some command back to the DTO to wait until the temperature
        is stable.
        """

    @abstractmethod
    def power_off(self):
        """Turn the cooler power off

        Must be implemented by hardware-specific Agent
        """
