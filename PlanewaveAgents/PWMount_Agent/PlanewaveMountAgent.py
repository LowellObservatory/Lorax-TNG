"""
Created on Feb 3, 2022

@author: dlytle

"""

import time
import logging
from typing_extensions import Self
import stomp
import yaml
import sys
import inspect
import os
import xmltodict
import uuid
import datetime

from PlanewaveMountTalk import PlanewaveMountTalk

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
from AbstractAgents.SubAgent import SubAgent

# Set stomp so it only logs WARNING and higher messages. (default is DEBUG)
logging.getLogger("stomp").setLevel(logging.WARNING)


class PlanewaveMountAgent(SubAgent):
    hosts = ""
    # log_file = ""
    mount_host = ""
    mount_port = 0
    current_message = ""
    message_received = 0
    mount_status = ""
    wait_list = ["gotoAltAz", "gotoRaDecJ2000", "homeMount", "parkMount"]

    def __init__(self, logger, conn, config):
        print("in PlanewaveMountAgent.init")
        SubAgent.__init__(self, logger, conn, config)

        # Tell em we've started.
        self.logger.info("Initializing: mount logging started")

        # Get the host and port for the connection to mount.
        self.mount_host = self.config["mount_host"]
        self.mount_port = self.config["mount_port"]

        self.planewave_mount_talk = PlanewaveMountTalk(
            self, host=self.mount_host, port=self.mount_port
        )
        print("got here")

    def get_status_and_broadcast(self):
        self.planewave_mount_talk.send_command_to_mount("status")
        time.sleep(0.01)
        mydict = {
            "mount_status": {
                "message_id": uuid.uuid4(),
                "timestamput": self.mount_status.response.timestamp_utc,
                "telescope": "TiMo",
                "device": {"type": "mount", "vendor": "planewave"},
                "is_slewing": self.mount_status.mount.is_slewing,
                "is_tracking": self.mount_status.mount.is_tracking,
                "azimuth": self.mount_status.mount.azimuth_degs,
                "altitude": self.mount_status.mount.altitude_degs,
                "RA-J2000": self.mount_status.mount.ra_j2000_hours,
                "dec-j2000": self.mount_status.mount.dec_j2000_degs,
                "rotator-angle": self.mount_status.rotator.field_angle_degs,
            }
        }
        xml_format = xmltodict.unparse(mydict, pretty=True)
        # print("/topic/" + pwma.config["broadcast_topic"])
        self.conn.send(
            body=xml_format,
            destination="/topic/" + self.config["broadcast_topic"],
        )

    class MyListener(stomp.ConnectionListener):
        def __init__(self, parent):
            self.parent = parent
            pass

        def on_error(self, message):
            print('received an error "%s"' % message)

        def on_message(self, message):
            # print('received a message "%s"' % message)

            self.parent.mount_logger.info('received a message "%s"' % message.body)
            self.parent.current_message = message.body
            self.parent.message_received = 1

    def handle_message(self, message):
        print("got message: in SBIGCcdCooler")
        print(message)

        # if pwma.current_message == "end":
        #     os._exit(0)
        # else:
        #     pwma.planewave_mount_talk.send_command_to_mount(pwma.current_message)
        self.planewave_mount_talk.send_command_to_mount(message)

        # If command in wait_list, send "Wait" to DTO, check status
        # until is_slewing is false, then send "Go" to DTO.
        if any(s in message for s in self.wait_list):
            # print("we are in a wait loop")
            # Send mount status back to DTO.
            self.conn.send(
                body="Wait",
                destination="/topic/" + self.config["dto_command_topic"],
            )
            # time.sleep(0.5)
            while True:
                self.get_status_and_broadcast()
                # print("is_slewing: ", pwma.mount_status.mount.is_slewing)
                if not self.mount_status.mount.is_slewing:
                    break

            self.conn.send(
                body="Go",
                destination="/topic/" + self.config["dto_command_topic"],
            )
            # time.sleep(0.5)
