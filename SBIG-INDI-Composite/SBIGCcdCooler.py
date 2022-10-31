# Built-In Libraries
import datetime
import time
import uuid

# 3rd Party Libraries
import numpy as np
import xmltodict

# Internal Imports
from IndiClient import IndiClient
from AbstractAgents.SubAgent import SubAgent


class SBIGCcdCooler(SubAgent):
    def __init__(self, logger, conn, config):
        print("in SBIGCcdCooler.init")
        SubAgent.__init__(self, logger, conn, config)
        # Get the host and port for the connection to cooler.
        # "config", in this case, is just a dictionary.
        self.indiclient = IndiClient(self, config)
        # print(self.config)
        self.indiclient.setServer(
            self.config["cooler_host"], self.config["cooler_port"]
        )
        self.device_status = {}

        self.indiclient.connectServer()

        device_ccd = self.indiclient.getDevice(self.config["cooler_name"])
        while not (device_ccd):
            time.sleep(0.5)
            device_ccd = self.indiclient.getDevice(self.config["cooler_name"])

        self.device_ccd = device_ccd

    def get_status_and_broadcast(self):
        c_status = {
            "message_id": uuid.uuid4(),
            "timestamput": datetime.datetime.utcnow(),
        }
        for key in self.device_status.keys():
            c_status[key] = self.device_status[key]

        status = {"ccdcooler": c_status}
        xml_format = xmltodict.unparse(status, pretty=True)

        print("/topic/" + self.config["outgoing_topic"])

        self.conn.send(
            body=xml_format,
            destination="/topic/" + self.config["outgoing_topic"],
        )

    def handle_message(self, message):
        print("got message: in SBIGCcdCooler")
        print(message)

        if "(" in message:
            mcom = message[0 : message.find("(")]
        else:
            mcom = message
        print(mcom)

        if mcom == "settemp":
            # Get the arguments.
            # setTemp(-45.0)
            print("doing settemp")
            com = message
            temperature = float(com[com.find("(") + 1 : com.find(")")])
            print("setting temp to " + str(temperature))
            temp = self.device_ccd.getNumber("CCD_TEMPERATURE")
            temp[0].value = np.float(temperature)  ### new temperature to reach
            self.indiclient.sendNewNumber(temp)

        elif mcom == "status":
            print("doing status")
            self.get_status_and_broadcast()

        # if "set_temp" in message:
        # send set temp.
        # send "wait" to DTO.
        # send specific command, "set temp", to ccd cooler
        # keep checking status until temp within limits.
        # send "go" command to DTO.
        # print("ccd cooler: set temp")
        # if "report_temp" in message:
        # report temp.
        # send specific command, "report temp", to ccd cooler
        # broadcast temp
        # print("ccd cooler: report temp")

        else:
            print("Unknown command")
