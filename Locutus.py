"""
Created on Aug 22, 2022

@author: dlytle

"""

import time
import logging
import xmltodict
import redis

from SpecialAgent import SpecialAgent

# Set stomp so it only logs WARNING and higher messages. (default is DEBUG)
logging.getLogger("stomp").setLevel(logging.WARNING)


class Locutus(SpecialAgent):
    def __init__(self, cfile):
        print("in Locutus.init")
        SpecialAgent.__init__(self, cfile)
        [redis_host, redis_port] = self.config["redis_host"]
        print("redis_host = " + redis_host)
        print("redis_port = " + str(redis_port))
        self.logger.info("Connecting to Redis at: " + redis_host)
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
        print("")
        print("message: ", end="")
        print(self.current_destination + ": ", end="")
        print(self.current_message)
        message_agent = self.current_destination.split(".")[2]
        print("message_agent = " + message_agent)
        agent = (
            self.config["agents_to_monitor"][self.agent_names.index(message_agent)]
        )[message_agent]
        storage_list = agent["storage"]
        print(storage_list)
        status_dict = xmltodict.parse(self.current_message)
        print("status_dict")
        print(status_dict)
        output_dict = {}
        for topic in storage_list:
            print(topic)
            print(status_dict)
            print("  ")
            key = message_agent + "_status"
            print("key = " + key)
            print(status_dict[key])
            print("  ")
            print(status_dict[key].keys())
            xyz = status_dict[key]
            print(type(xyz))
            for k, v in xyz.items():
                print(k)
                print(v)
                if k == topic:
                    output_dict[topic] = v
        self.redis_handle.hmset(message_agent + "Status", output_dict)
        dict_from_redis = self.redis_handle.hgetall(message_agent + "Status")
        print(dict_from_redis)

        # xml_message = self.current_message
        # if "mount" in self.current_destination:
        #     # Store mount status in Redis.
        #     # Decode the XML message into a python dictionary.
        #     status_dict = xmltodict.parse(xml_message)
        #     print(status_dict)

        #     # Based on the mount storage map, pick out pieces we need.
        #     # Storage maps are in config file.
        #     mount_store_list = self.config["mount_storage"]
        #     output_dict = {}
        #     for topic in mount_store_list:
        #         print(topic)
        #         print(status_dict)
        #         output_dict[topic] = (status_dict["mount_status"])[topic]
        #     # print(output_dict)
        #     self.redis_handle.hmset("mountStatus", output_dict)
        #     dict_from_redis = self.redis_handle.hgetall("mountStatus")
        #     print(dict_from_redis)

        # if "camera" in self.current_destination:
        #     # Store mount status in Redis.
        #     pass

        # if "weather" in self.current_destination:
        #     # Store weather status in Redis.
        #     pass

        if self.config["dictionary_request_topic"] in self.current_destination:
            # A dictionary has been requested, get dictionary details,
            # assemble dictionary, translate to XML and broadcast.
            self.assemble_dictionary_and_broadcast(locutus.current_message)

        # Wait a bit for another message
        time.sleep(self.config["message_wait_time"])


if __name__ == "__main__":
    locutus = Locutus("locutus.yaml")

    while True:
        if locutus.message_received:
            locutus.handle_message()
            locutus.message_received = 0
