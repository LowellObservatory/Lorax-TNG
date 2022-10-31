"""
Created on Aug. 30, 2022
@author: dlytle

"""
import logging
import stomp
import yaml
from abc import ABC, abstractmethod

# Set stomp so it only logs WARNING and higher messages. (default is DEBUG)
logging.getLogger("stomp").setLevel(logging.WARNING)

# General Agent class, inherit from Abstract Base Class
class Agent(ABC):
    hosts = ""
    log_file = ""
    current_message = ""
    message_received = 0

    def __init__(self, config_file):

        print("in agent.init")
        # Read the config file.
        with open(config_file, "r") as stream:
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
        self.hosts = [tuple(self.config["broker_hosts"])]
        self.logger.info("connecting to broker at " + str(self.config["broker_hosts"]))
        try:
            # Get a connection handle.
            self.conn = stomp.Connection(host_and_ports=self.hosts)

            # Set up a listener and and connect. Pass this class to listener.
            self.conn.set_listener("", self.BrokerListener(self))
            self.conn.connect(wait=True)
        except:
            self.logger.error("Connection to broker failed")
        self.logger.info("connected to broker")

        # Subscribe to messages from "incoming_topic"
        self.logger.info("subscribing to topic: " + self.config["incoming_topic"])
        self.conn.subscribe(
            id=1,
            destination="/topic/" + self.config["incoming_topic"],
            headers={},
        )
        self.logger.info("subscribed to topic " + self.config["incoming_topic"])

    @abstractmethod
    def get_status_and_broadcast(self):
        pass

    @abstractmethod
    def handle_message(self):
        pass

    class BrokerListener(stomp.ConnectionListener):
        def __init__(self, parent):
            self.parent = parent
            pass

        def on_error(self, message):
            print('received an error "%s"' % message)

        def on_message(self, message):
            # print('received a message "%s"' % message)

            self.parent.logger.info('received a message "%s"' % message.body)
            self.parent.current_message = message
            self.parent.message_received = 1
