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
        self.logger.info("Connecting to Redis at: " + self.config["redis_host"][0])
        self.redis_handle = redis.Redis(
            host=self.config["redis_host"][0], port=self.config["redis_host"][1]
        )
        # Subscribe to dictrequest and inforequest.
        self.broker_subscribe(self.config["dictionary_request_topic"])
        self.broker_subscribe(self.config["information_request_topic"])

    def broker_subscribe(self, topic):
        self.logger.info("subscribing to topic: " + topic)
        self.conn.subscribe(
            id=1,
            destination="/topic/" + topic,
            headers={},
        )
        self.logger.info("subscribed to topic " + topic)

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
        xml_message = self.current_message
        if "mount" in self.current_destination:
            # Store mount status in Redis.
            # Decode the XML message into a python dictionary.
            status_dict = xmltodict.parse(xml_message)
            print(status_dict)

            # Based on the mount storage map, pick out pieces we need.
            # Storage maps are in config file.
            mount_store_list = self.config["mount_storage"]
            output_dict = {}
            for topic in mount_store_list:
                print(topic)
                print(status_dict)
                output_dict[topic] = (status_dict["mount_status"])[topic]
            # print(output_dict)
            self.redis_handle.hmset("mountStatus", output_dict)
            dict_from_redis = self.redis_handle.hgetall("mountStatus")
            print(dict_from_redis)

        if "camera" in self.current_destination:
            # Store mount status in Redis.
            pass

        if "weather" in self.current_destination:
            # Store weather status in Redis.
            pass

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
