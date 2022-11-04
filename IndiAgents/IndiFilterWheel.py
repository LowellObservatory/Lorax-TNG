# Built-In Libraries
import datetime
import time
import uuid

# 3rd Party Libraries
import numpy as np
import xmltodict

# Internal Imports
from AbstractAgents import SubAgent
from IndiAgents.IndiClient import IndiClient


class IndiFilterWheel(SubAgent):
    """SBIG Filter Wheel SubAgent

    _extended_summary_

    Parameters
    ----------
    logger : _type_
        _description_
    conn : _type_
        _description_
    config : _type_
        _description_
    """

    def __init__(self, logger, conn, config):
        print("in SBIGFilterWheel.init")
        SubAgent.__init__(self, logger, conn, config)

        # Get the host and port for the connection to filter wheel.
        # "config", in this case, is just a dictionary.
        self.indiclient = IndiClient(self, config)
        self.indiclient.setServer(self.config["fw_host"], self.config["fw_port"])
        self.device_status = {}

        self.indiclient.connectServer()

        device_ccd = self.indiclient.getDevice(self.config["fw_name"])
        while not device_ccd:
            time.sleep(0.5)
            device_ccd = self.indiclient.getDevice(self.config["fw_name"])

        self.device_ccd = device_ccd

        # slot = self.device_ccd.getNumber("FILTER_SLOT")
        # print(slot)
        # slot[0].value = np.int(0)  # new position to reach
        # self.indiclient.sendNewNumber(slot)

        # ---------

        # List out the devices available from the INDI server
        devlist = [d.getDeviceName() for d in self.indiclient.getDevices()]
        print(f"This is the list of connected devices: {devlist}")

        # Check that the desired CCD is in the list of devices on the INDI server
        self.ccd = self.config["fw_name"]
        if self.ccd not in devlist:
            print(f"Warning: {self.ccd} not in the list of available INDI devices!")
            return

        # Get the device from the INDI server
        device_ccd = self.indiclient.getDevice(self.ccd)
        while not device_ccd:
            print("  Waiting on connection to the CCD Camera...")
            time.sleep(0.5)
            device_ccd = self.indiclient.getDevice(self.ccd)
        self.device_ccd = device_ccd
        # ----------

    def get_status_and_broadcast(self):
        c_status = {
            "message_id": uuid.uuid4(),
            "timestamput": datetime.datetime.utcnow(),
        }
        for key in self.device_status:
            c_status[key] = self.device_status[key]

        status = {"filterwheel": c_status}
        xml_format = xmltodict.unparse(status, pretty=True)

        print("/topic/" + self.config["outgoing_topic"])

        # print(xml_format)
        self.conn.send(
            body=xml_format,
            destination="/topic/" + self.config["outgoing_topic"],
        )

    def handle_message(self, message):
        print("got message: in SBIGFilterWheel")
        print(message)
        if "(" in message:
            mcom = message[0 : message.find("(")]
        else:
            mcom = message
        print(mcom)

        if "home" in message:
            # send wheel home.
            # send "wait" to DTO.
            # send specific command, "home", to filter wheel
            # keep checking status until done.
            # send "go" command to DTO.
            print("filter wheel: home")
        if "move" in message:
            # send wheel to specific position.
            # check arguments against position limits.
            # send "wait" to DTO.
            # send specific command, "movoto x", to filter wheel
            # keep checking status until done.
            # send "go" command to DTO.
            com = message
            position = int(com[com.find("(") + 1 : com.find(")")])
            print("setting position to " + str(position))
            slot = self.device_ccd.getNumber("FILTER_SLOT")
            slot[0].value = np.int(position)  # new position to reach
            self.indiclient.sendNewNumber(slot)
