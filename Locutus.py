"""
Created on Aug 22, 2022

@author: dlytle

"""

import time
import logging
import stomp
import yaml

from SpecialAgent import SpecialAgent

# Set stomp so it only logs WARNING and higher messages. (default is DEBUG)
logging.getLogger("stomp").setLevel(logging.WARNING)


class Locutus(SpecialAgent):
    def __init__(self, cfile):
        print("in Locutus.init")
        SpecialAgent.__init__(self, cfile)

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
        print(self.current_message.headers["destination"] + ": ", end="")
        print(self.current_message.body)
        if "mount" in self.current_destination:
            # Store camera status in Redis.
            pass

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

    class MyListener(stomp.ConnectionListener):
        def __init__(self, parent):
            self.parent = parent
            pass

        def on_error(self, message):
            print('received an error "%s"' % message)

        def on_message(self, message):
            # print('received a message "%s"' % message)

            self.parent.locutus_logger.info('received a message "%s"' % message.body)
            self.parent.current_destination = message.destination
            self.parent.current_message = message.body
            self.parent.message_received = 1


if __name__ == "__main__":
    locutus = Locutus()

    while True:
        if locutus.message_received:
            locutus.handle_message()
            locutus.message_received = 0
