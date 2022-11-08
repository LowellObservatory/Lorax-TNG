"""
Created on Sept. 19, 2022
@author: dlytle

"""
from abc import ABC, abstractmethod

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
