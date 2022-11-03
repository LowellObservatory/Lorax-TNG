"""
Created on Aept. 19, 2022
@author: dlytle

"""
import logging

import stomp
import yaml

# Set stomp so it only logs WARNING and higher messages. (default is DEBUG)
logging.getLogger("stomp").setLevel(logging.WARNING)

# General Composite Agent class
class CompositeAgent():
    """Composite Agent Class

    The ``config_file`` contains the information about which SubAgents will be
    instantiated to form the CompositeAgent.  In this way, the CompositeAgent
    components are defined only at runtime; CompositeAgents are not pre-
    constructed entities.  This allows flexibility with a minimal repitition of
    code.

    Parameters
    ----------
    config_file : :obj:`str` or :obj:`pathlib.Path`
        Filename of the configuration file to read in
    """

    hosts = ""
    log_file = ""
    current_message = ""
    current_destination = ""
    message_received = 0
    agents = []
    incoming_topics = []

    def __init__(self, config_file):

        print(" In CompositeAgent.__init__()")
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
        self.hosts = [tuple(self.config["broker_hosts"])]
        self.logger.info("connecting to broker at %s", self.config["broker_hosts"])
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
        for agent in agent_list:
            # print(f"Subscribing to broker topic for {agent}")
            this_topic = list(agent.values())[0]["incoming_topic"]
            self.incoming_topics.append(this_topic)
            self.broker_subscribe(this_topic)

        # Instantiate each of the sub-agents in the agent list.
        # Keep them in an array.
        for agent in agent_list:
            sub_agent = list(agent.values())[0]["agent_name"]
            protocol = list(agent.values())[0]["agent_protocol"]
            print(f"This is the SubAgent we want to instantiate: {protocol}.{sub_agent}")

            the_agent = __import__(f"{protocol}.{sub_agent}", fromlist=[sub_agent])
            the_agent = getattr(the_agent, sub_agent)
            self.agents.append(
                the_agent(self.logger, self.conn, list(agent.values())[0])
            )

    def broker_subscribe(self, topic):
        """Subscribe to a broker topic

        _extended_summary_

        Parameters
        ----------
        topic : str
            Broker topic to which to subscribe
        """
        print(f"CompositeAgent is subscribing to: {topic}")
        self.logger.info("subscribing to topic: %s", topic)
        self.conn.subscribe(
            id=1,
            destination="/topic/" + topic,
            headers={},
        )
        self.logger.info("subscribed to topic %s", topic)

    def get_status_and_broadcast(self):
        """Get status and broadcast on the broker

        _extended_summary_
        """
        # Send "get_status_and_broadcast" to each of the sub_agents.
        for agent in self.agents:
            agent.get_status_and_broadcast()

    def handle_message(self):
        """Handle incoming messages from the broker

        _extended_summary_
        """
        # This is the message's destination agent
        msg_destination = self.current_destination.rsplit(".", 1)[-1]

        # Loop through the list of "incoming topics" (i.e., "DTO -> Agent")
        # NOTE: Both self.incoming_topics and self.agents are lists in the same order
        for i, incoming_topic in enumerate(self.incoming_topics):
            if incoming_topic.rsplit(".", 1)[-1] == msg_destination:
                self.agents[i].handle_message(self.current_message)

    class BrokerListener(stomp.ConnectionListener):
        """STOMP broker listener

        _extended_summary_

        Parameters
        ----------
        parent : Class
            _description_
        """

        def __init__(self, parent):
            self.parent = parent

        def on_error(self, message):
            print(f'received an error "{message}"')

        def on_message(self, message):
            # print('received a message "%s"' % message)

            self.parent.logger.info('received a message "%s"', message.body)
            # self.parent.current_message = message
            self.parent.current_destination = message.headers["destination"]
            self.parent.current_message = message.body
            self.parent.message_received = 1
