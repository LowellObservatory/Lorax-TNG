"""
Created on Sept. 19, 2022
@author: dlytle

"""
from abc import ABC, abstractmethod
import datetime
import uuid

import xmltodict
import yaml

# General Sub-Agent class, inherit from Abstract Base Class
class SubAgent(ABC):
    """SubAgent

    _extended_summary_
    """

    def __init__(self, logger, conn, config):
        # print(config)
        self.logger = logger
        self.conn = conn
        self.config = config

    @abstractmethod
    def get_status_and_broadcast(self):
        """Get hardware status and broadcast on the broker

        Must be implemented by inheriting class.
        """

    @abstractmethod
    def handle_message(self, message):
        """Handle incoming messages from the broker

        Must be implemented by inheriting class.
        """

    def broadcast_status(self, device_status):
        """Broadcast the status packet from the device

        This method is common to all SubAgents.  It takes the ``device_status``
        from the protocol-specific Agent and packages it in a uniform manner
        for broadcasting.

        ..note::
            ``self.conn`` and ``self.config`` are required for instantiation
            of the protocol-specific Agent and are passed into this abstract
            class, and are the only pieces of ``self`` required for this
            method.

        Parameters
        ----------
        device_status : dict
            The device status dictionary to broadcast (may be empty)
        """
        # Type checking
        if not isinstance(device_status, dict):
            raise TypeError("`device_status` must be a dictionary")

        # Build the XML Status Packet
        status = {
            "message_id": uuid.uuid4(),
            "timestamput": datetime.datetime.utcnow(),
            "sender": self.__class__.__name__,
            "status": device_status,
        }
        xml_format = xmltodict.unparse({"root": status}, pretty=True)

        # Broadcast
        self.conn.send(
            body=xml_format,
            destination="/topic/" + self.config["outgoing_topic"],
        )
