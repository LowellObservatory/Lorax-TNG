"""
Created on Sept. 7, 2022

@author: dlytle

"""

from abc import ABC, abstractmethod
import logging

import stomp
import yaml


# Set stomp so it only logs WARNING and higher messages. (default is DEBUG)
logging.getLogger("stomp").setLevel(logging.WARNING)

# Special Agent class, inherit from Abstract Base Class
class SpecialAgent(ABC):
    """Special Agent (Abstract)

    _extended_summary_

    Parameters
    ----------
    ABC : _type_
        _description_
    """

    host = ""
    log_file = ""
    current_message = ""
    message_received = 0

    def __init__(self, config_file):

        print("in special_agent.init")
        # Read the config file.
        with open(config_file, "r", encoding="utf-8") as stream:
            try:
                self.config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        # Get the log file name from the configuration.
        # Set up the logger.
        self.log_file = self.config["log_file"]
        logging.basicConfig(
            filename=self.log_file,
            format="%(asctime)s %(levelname)-8s %(message)s",
            level=logging.DEBUG,
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        self.logger = logging.getLogger("agent_log")

        # Tell em we've started.
        self.logger.info("Initializing: logging started")

        # Get the broker host from the configuration.
        # Make a connection to the broker.
        self.host = [tuple(self.config["broker_host"])]
        self.logger.info("connecting to broker at %s", str(self.config["broker_host"]))
        try:
            # Get a connection handle.
            self.conn = stomp.Connection(host_and_ports=self.host)

            # Set up a listener and and connect. Pass this class to listener.
            self.conn.set_listener("", self.BrokerListener(self))
            self.conn.connect(wait=True)
        except:
            self.logger.error("Connection to broker failed")
        self.logger.info("connected to broker")

        # Subscribe to topics in each agent description in "agents_to_monitor".
        agent_list = self.config["agents_to_monitor"]
        for agent in agent_list:
            print(agent)
            this_topic = list(agent.values())[0]["incoming_topic"]
            self.broker_subscribe(this_topic)

    def broker_subscribe(self, topic):
        """Subscribe to broker topic

        _extended_summary_

        Parameters
        ----------
        topic : _type_
            _description_
        """
        self.logger.info("subscribing to topic: %s", topic)
        self.conn.subscribe(
            id=1,
            destination="/topic/" + topic,
            headers={},
        )
        self.logger.info("subscribed to topic %s", topic)

    @abstractmethod
    def handle_message(self):
        """Handle message from broker

        _extended_summary_
        """

    class BrokerListener(stomp.ConnectionListener):
        """Broker Listener Class

        _extended_summary_

        Parameters
        ----------
        stomp : _type_
            _description_
        """

        def __init__(self, parent):
            self.parent = parent

        def on_error(self, message):
            print(f'received an error "{message}"')

        def on_message(self, message):
            # print('received a message "%s"' % message)

            self.parent.logger.info(f'received a message "{message.body}"')
            # print(message.headers["destination"])
            self.parent.current_destination = message.headers["destination"]
            self.parent.current_message = message.body
            self.parent.message_received = 1
