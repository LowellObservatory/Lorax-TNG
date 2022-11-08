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

        if "init" in message:
            print("Connecting to the cooler...")
            self.connect_to_cooler()

        elif "disconnect" in message:
            print("Disconnecting from cooler...")
            self.disconnect_from_cooler()
            self.cooler = None
            self.device_cooler = None

        elif "status" in message:
            # print("doing status")
            self.get_status_and_broadcast()

        elif "set_temperature" in message:
            # Get the arguments.
            # setTemp(-45.0)
            # print("doing settemp")
            com = message
            temperature = float(com[com.find("(") + 1 : com.find(")")])
            self.set_temperature(temperature)
            print(f"Temperature set to {temperature:.1f}ºC")

        elif "set_temp_tolerance" in message:
            print("cooler: set_temp_tolerance (no effect)")

        elif "power_off" in message:
            print("cooler: power_off (no effect)")

        elif "power_on" in message:
            print("cooler: power_on (no effect)")

        else:
            warnings.warn("Unknown command")

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

        Should have some command back to the DTO to wait until the temperature
        is stable.
        """
        raise NotImplementedError("Specific hardware Agent must implement this method.")
