"""
Created on Aug 22, 2022

@author: dlytle

"""
import inspect
import logging
import time
import os
import sys

import redis
import xmltodict

from AbstractAgents.SpecialAgent import SpecialAgent

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)

# Set stomp so it only logs WARNING and higher messages. (default is DEBUG)
logging.getLogger("stomp").setLevel(logging.WARNING)


class Locutus(SpecialAgent):
    def __init__(self, cfile):
        print("in Locutus.init")
        SpecialAgent.__init__(self, cfile)
        self.message_received = 0
        self.current_destination = ""
        [redis_host, redis_port] = self.config["redis_host"]
        print("redis_host = " + redis_host)
        print("redis_port = " + str(redis_port))
        self.logger.info("Connecting to Redis at: %s", redis_host)
        self.redis_handle = redis.Redis(host=redis_host, port=redis_port)
        # Subscribe to dictrequest and inforequest.
        self.broker_subscribe(self.config["dictionary_request_topic"])
        self.broker_subscribe(self.config["information_request_topic"])

        # Get a list of the agents.
        self.agent_names = []
        for agent in self.config["agents_to_monitor"]:
            self.agent_names.append(list(agent.keys())[0])

    def assemble_dictionary_and_broadcast(self, dict_requested):
        this_dict = self.gather_dictionary(dict_requested)
        xml_dictionary = self.dict_to_xml(this_dict)
        self.conn.send(
            body=xml_dictionary,
            destination="/topic/" + locutus.config["dictionary_broadcast_topic"],
        )

    def gather_dictionary(self, dict_requested):
        this_dict = dict_requested + "xyz"
        return this_dict

    def dict_to_xml(self, this_dict):
        xml_dict = this_dict + "xyz"
        return xml_dict

    def handle_message(self):
        # Get the agent from the topic.
        message_agent = self.current_destination.split(".")[2]
        # Get the Agent.
        agent = (
            self.config["agents_to_monitor"][self.agent_names.index(message_agent)]
        )[message_agent]

        # Get the list of items to store in Redis for this agent.
        storage_list = agent["storage"]

        # Get the dictionary of stuff from the message.
        status_dict = xmltodict.parse(self.current_message)
        # Get the sub-dictionary containing agent_status.
        status_dict = status_dict[message_agent + "_status"]

        # Construct a dictionary of key-value pairs to go in Redis.
        output_dict = {}
        for topic in storage_list:
            try:
                output_dict[topic] = status_dict[topic]
            except KeyError:
                print(topic + " not found in status message")

        self.redis_handle.hmset(message_agent + "Status", output_dict)
        dict_from_redis = self.redis_handle.hgetall(message_agent + "Status")
        print(dict_from_redis)

        if self.config["dictionary_request_topic"] in self.current_destination:
            # A dictionary has been requested, get dictionary details,
            # assemble dictionary, translate to XML and broadcast.
            self.assemble_dictionary_and_broadcast(locutus.current_message)

        # Wait a bit for another message
        time.sleep(self.config["message_wait_time"])


if __name__ == "__main__":
    locutus = Locutus("Locutus/locutus.yaml")

    while True:
        if locutus.message_received:
            locutus.handle_message()
            locutus.message_received = 0
