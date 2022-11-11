# Built-In Libraries
import datetime
import time
import uuid

# 3rd Party Libraries
import numpy as np
import xmltodict

# Internal Imports
from AbstractAgents.FilterWheelSubAgent import FilterWheelSubAgent
from IndiAgents.IndiClient import IndiClient


class IndiFilterWheel(FilterWheelSubAgent):
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
        super().__init__(logger, conn, config)

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

    def move(self, position):
        """Move the filter wheel"""
        print(f"Setting filter wheel position to {position}")
        slot = self.device_filterwheel.getNumber("FILTER_SLOT")
        slot[0].value = int(position)  # new position to reach
        self.indiclient.sendNewNumber(slot)
