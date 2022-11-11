# -*- coding: utf-8 -*-
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
#  Created on 08-Nov-2022
#
#  @author: dlytle, tbowers

"""Lorax Rotator SubAgent Abstract Class

This module is part of the Lorax-TNG package, written at Lowell Observatory.

This SubAgent is to be inherited by all protocol-based Rotator Agents, and
provides the complete API for all Lorax Rotator Agents (contained in the
:func:`handle_message` method).

The Lorax Rotator API is as follows:
===================================

    init
        Initialize and connect to the rotator
    disconnect
        Disconnect from the rotator
    status
        Broadcast the current status of the rotator
    home
        Home the rotator
    stop
        Stop rotator motion
    goto_field
        Go to the field rotation angle specified by the mount
    goto_mech
        Go to a specified mechanical rotator angle
    offset
        Apply the specified offset to the rotator

"""

# Built-In Libraries
from abc import abstractmethod
import warnings

# 3rd Party Libraries

# Internal Imports
from AbstractAgents.SubAgent import SubAgent
from CommandLanguage import parse_dscl


class RotatorSubAgent(SubAgent):
    """Rotator SubAgent

    This SubAgent contains the methods common to all ROTATOR instances,
    regardless of the hardware communication protocol.  Namely, the populated
    methods contained herein merely set instance attributes and do not
    communicate directly with the hardware.  Also, this class handles all of
    the rotator message commands, to minimize replication between pieces of hardware.

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
        self.rotator = None
        self.device_rotator = None

    def handle_message(self, message):
        """Handle an incoming message

        This method contains the API for the RotatorSubAgent.  Incoming
        messages are compared against the command list, and the proper method
        is called.  Some of the API commands are general to all Rotator Agents
        and are fully implemented here; others are hardware-specific and are
        left as abstract methods for later implementation.

        Parameters
        ----------
        message : str
            The incoming message from the broker, as passed down from the
            Composite Agent.
        """
        print(f"\nReceived message in RotatorSubAgent: {message}")

        # Parse out the message
        command, arguments = parse_dscl.parse_command(message)

        if command == "init":
            print("Connecting to the rotator...")
            self.connect_to_rotator()

        elif command == "disconnect":
            print("Disconnecting from rotator...")
            self.disconnect_from_rotator()

        elif command == "home":
            # send mount home.
            # send "wait" to DTO.
            # send specific command, "home", to filter wheel
            # keep checking status until done.
            # send "go" command to DTO.
            print("rotator: home (no effect)")

        elif command == "stop":
            print("rotator: stop (no effect)")

        elif command == "goto_field":
            print("rotator: goto_field (no effect)")

        elif command == "goto_mech":
            print("rotator: goto_mech (no effect)")

        elif command == "offset":
            print("rotator: offset (no effect)")

        else:
            warnings.warn(f"Unknown command: {command}")

    def get_status_and_broadcast(self):
        """Get the current rotator status and broadcast it

        _extended_summary_
        """
        # Check if the cooler is connected; get status or set empty dictionary
        device_status = self.device_status if self.device_rotator.isConnected() else {}
        # Broadcast
        self.broadcast_status(device_status)

    def check_rotator_connection(self):
        """Check that the client is connected to the rotator
        Returns
        -------
        ``bool``
            Whether the rotator is connected
        """
        if self.device_rotator and self.device_rotator.isConnected():
            return True

        print("Warning: Mount must be connected first (rotator : connect_to_rotator)")
        return False

    @abstractmethod
    def connect_to_rotator(self):
        """Connect to rotator

        Must be implemented by hardware-specific Agent
        """

    @abstractmethod
    def disconnect_from_rotator(self):
        """Disconnect from rotator

        Must be implemented by hardware-specific Agent
        """

    @abstractmethod
    def move(self, slot):
        """Move the rotator

        Must be implemented by hardware-specific Agent
        """

    @abstractmethod
    def home(self):
        """Home the mount

        Must be implemented by hardware-specific Agent
        """
