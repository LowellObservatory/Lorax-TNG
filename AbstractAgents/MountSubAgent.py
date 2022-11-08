# -*- coding: utf-8 -*-
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
#  Created on 08-Nov-2022
#
#  @author: dlytle, tbowers

"""Lorax Mount SubAgent Abstract Class

This module is part of the Lorax-TNG package, written at Lowell Observatory.

This SubAgent is to be inherited by all protocol-based Mount Agents, and
provides the complete API for all Lorax Mount Agents (contained in the
:func:`handle_message` method).

The Lorax Mount API is as follows:
===================================

    init
        Initialize and connect to the mount
    disconnect
        Disconnect from the mount
    status
        Broadcast the current status of the mount
    park
        Park the mount
    stop
        Stop mount motion
    track_sidereal
        Track the telescope at the sidereal rate
    track_ephemeris
        Track the telescope according to the supplied ephemeris
    goto_ra_dec_apparent
        Go to apparent RA/Dec location
    goto_ra_dec_j2000    
        Go to the J2000 RA/Dec location
    goto_alt_az
        Go to the ALT/AZ location
    offset
        Apply the specified offset

"""

# Built-In Libraries
from abc import abstractmethod
import warnings

# 3rd Party Libraries

# Internal Imports
from AbstractAgents.SubAgent import SubAgent


class MountSubAgent(SubAgent):
    """Mount SubAgent

    This SubAgent contains the methods common to all MOUNT instances,
    regardless of the hardware communication protocol.  Namely, the populated
    methods contained herein merely set instance attributes and do not
    communicate directly with the hardware.  Also, this class handles all of
    the mount message commands, to minimize replication between pieces of
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
        self.mount = None
        self.device_mount = None

    def handle_message(self, message):
        """Handle an incoming message

        This method contains the API for the MountSubAgent.  Incoming
        messages are compared against the command list, and the proper method
        is called.  Some of the API commands are general to all Mount Agents
        and are fully implemented here; others are hardware-specific and are
        left as abstract methods for later implementation.

        Parameters
        ----------
        message : str
            The incoming message from the broker, as passed down from the
            Composite Agent.
        """
        print(f"\nReceived message in MountSubAgent: {message}")

        if "init" in message:
            print("Connecting to the mount...")
            self.connect_to_mount()

        elif "disconnect" in message:
            print("Disconnecting from mount...")
            self.disconnect_from_mount()

        elif "park" in message:
            # send mount to the park.
            # send "wait" to DTO.
            # send specific command, "park", to mount
            # keep checking status until done.
            # send "go" command to DTO.
            print("mount: park (no effect)")

        elif "move" in message:
            # send mount to specific position.
            # check arguments against position limits.
            # send "wait" to DTO.
            # send specific command, "movoto x", to filter wheel
            # keep checking status until done.
            # send "go" command to DTO.
            print("mount: move")

        elif "stop" in message:
            print("mount: stop (no effect)")

        elif "track_sidereal" in message:
            print("mount: track_sidereal (no effect)")

        elif "track_ephemeris" in message:
            print("mount: track_ephemeris (no effect)")

        elif "goto_ra_dec_apparent" in message:
            print("mount: goto_ra_dec_apparent (no effect)")

        elif "goto_ra_dec_j2000" in message:
            print("mount: goto_ra_dec_j2000 (no effect)")

        elif "goto_alt_az" in message:
            print("mount: goto_alt_az (no effect)")

        elif "offset" in message:
            print("mount: offset (no effect)")

        else:
            warnings.warn("Unknown command")

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
    def park(self):
        """Park the mount

        Must be implemented by hardware-specific Agent
        """
        raise NotImplementedError("Specific hardware Agent must implement this method.")
