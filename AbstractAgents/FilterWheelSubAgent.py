# -*- coding: utf-8 -*-
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
#  Created on 08-Nov-2022
#
#  @author: dlytle, tbowers

"""Lorax Filter Wheel SubAgent Abstract Class

This module is part of the Lorax-TNG package, written at Lowell Observatory.

This SubAgent is to be inherited by all protocol-based FilterWheel Agents, and
provides the complete API for all Lorax FilterWheen Agents (contained in the
:func:`handle_message` method).

The Lorax Filter Wheel API is as follows:
===================================

    init
        Initialize and connect to the filter wheel
    disconnect
        Disconnect from the filter wheel
    status
        Broadcast the current status of the filter wheel
    home
        Home the filter wheel
    move
        Move the filter wheel to a specified slot

"""

# Built-In Libraries
from abc import abstractmethod
import warnings

# 3rd Party Libraries

# Internal Imports
from AbstractAgents.SubAgent import SubAgent
from CommandLanguage import parse_dscl


class FilterWheelSubAgent(SubAgent):
    """Filter Wheel SubAgent

    This SubAgent contains the methods common to all FILTER WHEEL instances,
    regardless of the hardware communication protocol.  Namely, the populated
    methods contained herein merely set instance attributes and do not
    communicate directly with the hardware.  Also, this class handles all of
    the filter wheel message commands, to minimize replication between pieces
    of hardware.

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
        """Handle an incoming message

        This method contains the API for the FilterWheelSubAgent.  Incoming
        messages are compared against the command list, and the proper method
        is called.  Some of the API commands are general to all Filter Wheel
        Agents and are fully implemented here; others are hardware-specific and
        are left as abstract methods for later implementation.

        Parameters
        ----------
        message : str
            The incoming message from the broker, as passed down from the
            Composite Agent.
        """
        print(f"\nReceived message in FilterWheelSubAgent: {message}")

        # Parse out the message
        command, arguments = parse_dscl.parse_command(message)

        if command == "init":
            print("Connecting to the filter wheel...")
            self.connect_to_filterwheel()

        elif command == "disconnect":
            print("Disconnecting from filter wheel...")
            self.disconnect_from_filterwheel()

        elif command == "status":
            # print("doing status")
            self.get_status_and_broadcast()

        elif command == "home":
            # send wheel home.
            # send "wait" to DTO.
            # send specific command, "home", to filter wheel
            # keep checking status until done.
            # send "go" command to DTO.
            print("filter wheel: home (no effect)")

        elif command == "move":
            # send wheel to specific position.
            # check arguments against position limits.
            # send "wait" to DTO.
            # send specific command, "movoto x", to filter wheel
            # keep checking status until done.
            # send "go" command to DTO.
            print("filter wheel: move (no effect)")

        else:
            warnings.warn(f"Unknown command: {command}")

    def get_status_and_broadcast(self):
        """Get the current filter wheel status and broadcast it

        _extended_summary_
        """
        # Check if the cooler is connected; get status or set empty dictionary
        device_status = (
            self.device_status if self.device_filterwheel.isConnected() else {}
        )
        # Broadcast
        self.broadcast_status(device_status)

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

    @abstractmethod
    def disconnect_from_filterwheel(self):
        """Disconnect from filter wheel

        Must be implemented by hardware-specific Agent
        """

    @abstractmethod
    def home(self):
        """Home the filter wheel

        Must be implemented by hardware-specific Agent
        """

    @abstractmethod
    def move(self, slot):
        """Move the filter wheel

        Must be implemented by hardware-specific Agent
        """
