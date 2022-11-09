# -*- coding: utf-8 -*-
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
#  Created on 08-Nov-2022
#
#  @author: dlytle, tbowers

"""Lorax Dome SubAgent Abstract Class

This module is part of the Lorax-TNG package, written at Lowell Observatory.

This SubAgent is to be inherited by all protocol-based Dome Agents, and
provides the complete API for all Lorax Dome Agents (contained in the
:func:`handle_message` method).

The Lorax Dome API is as follows:
===================================

    init
        Initialize and connect to the dome
    disconnect
        Disconnect from the dome
    status
        Broadcast the current status of the dome
    home
        Home the dome
    move
        Move the dome to a specified azimuth
    track_mount
        Track the mount in azimuth
    stop_tracking
        Stop tracking the mount and stay in this position
    open_shutter
        Open the dome shutter
    close_shutter
        Close the dome shutter

"""

# Built-In Libraries
from abc import abstractmethod
import warnings

# 3rd Party Libraries

# Internal Imports
from AbstractAgents.SubAgent import SubAgent
from CommandLanguage import parse_dscl


class DomeSubAgent(SubAgent):
    """Dome SubAgent

    This SubAgent contains the methods common to all DOME instances,
    regardless of the hardware communication protocol.  Namely, the populated
    methods contained herein merely set instance attributes and do not
    communicate directly with the hardware.  Also, this class handles all of
    the dome message commands, to minimize replication between pieces of
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
        self.dome = None
        self.device_dome = None

    def handle_message(self, message):
        """Handle an incoming message

        This method contains the API for the DomeSubAgent.  Incoming
        messages are compared against the command list, and the proper method
        is called.  Some of the API commands are general to all Dome Agents
        and are fully implemented here; others are hardware-specific and are
        left as abstract methods for later implementation.

        Parameters
        ----------
        message : str
            The incoming message from the broker, as passed down from the
            Composite Agent.
        """
        print(f"\nReceived message in DomeSubAgent: {message}")

        # Parse out the message; check it went to the right place
        target, command, arguments = parse_dscl.parse_command(message)
        if target not in ["dome", "allserv"]:
            raise ValueError("NON-DOME command sent to dome!")

        if command == "init":
            print("Connecting to the dome...")
            self.connect_to_dome()

        elif command == "disconnect":
            print("Disconnecting from dome...")
            self.disconnect_from_dome()

        elif command == "status":
            # print("doing status")
            self.get_status_and_broadcast()

        elif command == "home":
            # send dome home.
            # send "wait" to DTO.
            # send specific command, "home", to filter wheel
            # keep checking status until done.
            # send "go" command to DTO.
            print("dome: home")

        elif command == "move":
            # send dome to specific position.
            # check arguments against position limits.
            # send "wait" to DTO.
            # send specific command, "movoto x", to filter wheel
            # keep checking status until done.
            # send "go" command to DTO.
            print("dome: move")

        elif command == "track_mount":
            print("dome: track_mount (no effect)")

        elif command == "stop_tracking":
            print("dome: stop_tracking (no effect)")

        elif command == "open_shutter":
            print("dome: open_shutter (no effect)")

        elif command == "close_shutter":
            print("dome: close_shutter (no effect)")

        else:
            warnings.warn(f"Unknown command: {command}")

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
    def home(self):
        """Home the dome

        Must be implemented by hardware-specific Agent
        """
        raise NotImplementedError("Specific hardware Agent must implement this method.")

    @abstractmethod
    def move(self, azimuth):
        """Move the dome

        Must be implemented by hardware-specific Agent
        """
        raise NotImplementedError("Specific hardware Agent must implement this method.")
