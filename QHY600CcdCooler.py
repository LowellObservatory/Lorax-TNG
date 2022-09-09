# -*- coding: utf-8 -*-
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
#  Created on 21-Oct-2022
#
#  @author: dlytle, tbowers

"""Lorax CCD Cooler Agent for the QHY 600M CMOS Camera

This module is part of the Lorax-TNG package, written at Lowell Observatory.

This CCD Cooler Agent concerns itself with the cooler aspects of the QHY600M, and
its functionality is called from the QHY600Composite module.

Hardware control of the QHY 600M is accomplished through an INDI interface,
contained in the HardwareClients module.
"""

# Built-In Libraries
import datetime
import sys
import time
import uuid

# 3rd Party Libraries
import PyIndi
import numpy as np
import xmltodict

# Internal Imports
from HardwareClients import IndiClient
from SubAgent import SubAgent


class QHY600CcdCooler(SubAgent):
    """QHY600M CCD Cooler Agent (SubAgent to QHY600Composite)

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
        print("in QHY600CcdCooler.init")
        SubAgent.__init__(self, logger, conn, config)
        # Get the host and port for the connection to mount.
        # "config", in this case, is just a dictionary.
        self.indiclient = IndiClient(self)
        # print(self.config)
        self.indiclient.setServer(
            self.config["cooler_host"], self.config["cooler_port"]
        )
        self.device_status = {}

        self.indiclient.connectServer()

        device_ccd = self.indiclient.getDevice(self.config["cooler_name"])
        while not device_ccd:
            time.sleep(0.5)
            device_ccd = self.indiclient.getDevice(self.config["cooler_name"])

        self.device_ccd = device_ccd

        # Define other instance attributes for later population
        self.ccd = None

    def get_status_and_broadcast(self):

        # print(self.device_status)
        print("cooler status")

        c_status = {
            "message_id": uuid.uuid4(),
            "timestamput": datetime.datetime.utcnow(),
            "root": self.device_status,
        }
        status = {"root": c_status}
        xml_format = xmltodict.unparse(status, pretty=True)

        print("/topic/" + self.config["outgoing_topic"])

        self.conn.send(
            body=xml_format,
            destination="/topic/" + self.config["outgoing_topic"],
        )

    def handle_message(self, message):
        print("got message: in QHY600CcdCooler")
        print(message)

        if "(" in message:
            mcom = message[0 : message.find("(")]
        else:
            mcom = message
        print(mcom)

        if mcom == "connect_to_cooler":
            print("doing connect_to_cooler")
            self.connect_to_cooler()

        if mcom == "settemp":
            # Get the arguments.
            # setTemp(-45.0)
            print("doing settemp")
            com = message
            temperature = float(com[com.find("(") + 1 : com.find(")")])
            print("setting temp to " + str(temperature))
            self.set_temperature(temperature)

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

    def connect_to_cooler(self):
        """Connect to the cooler

        Connect to the CCD cooler control.
        """
        # List out the devices available from the INDI server
        devlist = [d.getDeviceName() for d in self.indiclient.getDevices()]
        print(f"This is the list of connected devices: {devlist}")

        # Check that the desired CCD is in the list of devices on the INDI server
        self.ccd = self.config["cooler_name"]
        if self.ccd not in devlist:
            print(f"Warning: {self.ccd} not in the list of available INDI devices!")
            return

        # Get the device from the INDI server
        device_ccd = self.indiclient.getDevice(self.ccd)
        while not device_ccd:
            print("  Waiting on connection to the CMOS Camera...")
            time.sleep(0.5)
            device_ccd = self.indiclient.getDevice(self.ccd)
        self.device_ccd = device_ccd

        # Make the connection -- exit if no connection
        ccd_connect = self.device_ccd.getSwitch("CONNECTION")
        while not ccd_connect:
            print("not connected")
            time.sleep(0.5)
            ccd_connect = self.device_ccd.getSwitch("CONNECTION")
        while not device_ccd.isConnected():
            print("still not connected")
            ccd_connect[0].s = PyIndi.ISS_ON  # the "CONNECT" switch
            ccd_connect[1].s = PyIndi.ISS_OFF  # the "DISCONNECT" switch
            self.indiclient.sendNewSwitch(ccd_connect)
            time.sleep(0.5)
        print(f"Are we connected yet? {self.device_ccd.isConnected()}")
        if not self.device_ccd.isConnected():
            sys.exit()

        # Print a happy acknowledgment
        print(f"The Agent is now connected to {self.ccd}")

        # Tell the INDI server send the "CCD1" blob to this client
        self.indiclient.setBLOBMode(PyIndi.B_ALSO, self.ccd, "CCD1")

    def set_temperature(self, cool_temp, tolerance=1.0):
        """Set the cooler temperature

        Set the temperature goal of the cooler.  For the QHY600M, this also
        turns on the cooler power.

        Parameters
        ----------
        cool_temp : ``float``
            The desired cooler set point in degrees Celsius
        tolerance : ``float``
            Tolerance between CCD temperature and ``cool_temp`` before issuing
            a "Go" command to the DTO.
        """
        if not self.check_cooler_connection():
            return
        print(f"QHY600 Setting Cooler Temperature to {cool_temp:.1f}ºC")

        # Get the number vector property, set the new value, and send it back
        temp = self.device_ccd.getNumber("CCD_TEMPERATURE")
        temp[0].value = float(cool_temp)  ### new temperature to reach
        self.indiclient.sendNewNumber(temp)

        # NOTE: This should probably also send a "Wait" command back to the DTO
        #       and should quietly loop until either the temperature reaches
        #       the requested value or a timeout is reached.
        self.conn.send(body="Wait", destination="/topic/" + self.config["dto_topic"])

        ccd_cooler_temp = self.device_status["CCD_TEMPERATURE"]["vals"][0][1]
        ccd_cooler_powr = self.device_status["CCD_COOLER_POWER"]["vals"][0][1]

        print(
            f"Temperature difference: {np.abs(ccd_cooler_temp - cool_temp)}  Tolerance: {tolerance}   IF conditional: {np.abs(ccd_cooler_temp - cool_temp) > tolerance}"
        )

        while np.abs(ccd_cooler_temp - cool_temp) > tolerance:
            temp = self.device_ccd.getNumber("CCD_TEMPERATURE")
            temp[0].value = float(cool_temp)  ### new temperature to reach
            self.indiclient.sendNewNumber(temp)

            time.sleep(1.0)
            ccd_cooler_temp = self.device_status["CCD_TEMPERATURE"]["vals"][0][1]
            ccd_cooler_powr = self.device_status["CCD_COOLER_POWER"]["vals"][0][1]
            print(
                f"CCD Temp: {ccd_cooler_temp:.1f}ºC  "
                f"Set point: {cool_temp:.1f}ºC  "
                f"Cooler Power: {ccd_cooler_powr:.0f}%"
            )
        print(
            f"Cooler is stable at {ccd_cooler_temp:.1f}ºC, cooler power: {ccd_cooler_powr:.0f}%"
        )
        self.conn.send(body="Go", destination="/topic/" + self.config["dto_topic"])

    def check_cooler_connection(self):
        """Check that the client is connected to the camera

        Returns
        -------
        ``bool``
            Whether the camera is connected
        """
        if self.device_ccd and self.device_ccd.isConnected():
            return True

        print(
            "Warning: CCD Cooler must be connected first (cooler : connect_to_cooler)"
        )
        return False
