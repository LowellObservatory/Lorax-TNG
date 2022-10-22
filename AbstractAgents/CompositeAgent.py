"""
Created on Aept. 19, 2022
@author: dlytle

"""
import logging
import stomp
import yaml
import string
from abc import ABC, abstractmethod

# Set stomp so it only logs WARNING and higher messages. (default is DEBUG)
logging.getLogger("stomp").setLevel(logging.WARNING)

# General Composite Agent class, inherit from Abstract Base Class
class CompositeAgent(ABC):
    hosts = ""
    log_file = ""
    current_message = ""
    current_destination = ""
    message_received = 0
    agents = []
    incoming_topics = []

    def __init__(self, config_file):

        print("in composite_agent.init")
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

        # For each agent in list, subscribe to agent "incoming_topic".
        agent_list = self.config["agents_in_composite"]
        # print("agent_list")
        # print(agent_list)
        for agent in agent_list:
            # print(agent)
            this_topic = list(agent.values())[0]["incoming_topic"]
            self.incoming_topics.append(this_topic)
            self.broker_subscribe(this_topic)

        # Create each of the sub-agents in the agent list.
        # Keep them in an array.
        for agent in agent_list:
            sub_agent = list(agent.values())[0]["agent_name"]
            the_agent = __import__(sub_agent, fromlist=[sub_agent])
            the_agent = getattr(the_agent, sub_agent)
            self.agents.append(
                the_agent(self.logger, self.conn, list(agent.values())[0])
            )

    def broker_subscribe(self, topic):
        print(topic)
        self.logger.info("subscribing to topic: " + topic)
        self.conn.subscribe(
            id=1,
            destination="/topic/" + topic,
            headers={},
        )
        self.logger.info("subscribed to topic " + topic)

    @abstractmethod
    def get_status_and_broadcast(self):
        # Send "get_status_and_broadcast" to each of the sub_agents.
        for agent in self.agents:
            agent.get_status_and_broadcast(self)

    def handle_message(self):
        # Look up which agent the message is addressed to and send to that agent.
        i = 0
        agent_position = -1

        # Match the topic of the message in the incoming_topics list.
        while i < len(self.incoming_topics):
            compare_1 = self.current_destination.rsplit(".", 1)[-1]
            compare_2 = self.incoming_topics[i].rsplit(".", 1)[-1]
            # print(compare_1)
            # print(compare_2)
            if compare_1 == compare_2:
                # print("found it!")
                # print(i)
                agent_position = i
            i = i + 1
        # print("agent_position")
        # print(agent_position)
        if agent_position != -1:
            # If we found the topic, send the current message to the
            # corresponding agent.
            # print(len(self.agents))
            # print(self.current_message)
            self.agents[agent_position].handle_message(self.current_message)

    class BrokerListener(stomp.ConnectionListener):
        def __init__(self, parent):
            self.parent = parent
            pass

        def on_error(self, message):
            print('received an error "%s"' % message)

        def on_message(self, message):
            # print('received a message "%s"' % message)

            self.parent.logger.info('received a message "%s"' % message.body)
            # self.parent.current_message = message
            self.parent.current_destination = message.headers["destination"]
            self.parent.current_message = message.body
            self.parent.message_received = 1