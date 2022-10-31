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
from IndiClient import IndiClient
from SubAgent import CcdCoolerSubAgent


class QHY600CcdCooler(CcdCoolerSubAgent):
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
        print("   ---> Initializing the QHY600 Cooler SubAgent")
        super().__init__(logger, conn, config)
        # Get the host and port for the connection to mount.
        # "config", in this case, is just a dictionary.
        self.indiclient = IndiClient(self, config)
        # print(self.config)
        self.indiclient.setServer(
            self.config["cooler_host"], self.config["cooler_port"]
        )
        self.device_status = {}

        self.indiclient.connectServer()

        device_cooler = self.indiclient.getDevice(self.config["cooler_name"])
        while not device_cooler:
            time.sleep(0.5)
            device_cooler = self.indiclient.getDevice(self.config["cooler_name"])

        self.device_cooler = device_cooler

        # Define other instance attributes for later population
        self.cooler = None

    def get_status_and_broadcast(self):

        # Check if the cooler is connected
        device_status = (
            self.device_status
        )  # if self.device_cooler.isConnected() else {}

        c_status = {
            "message_id": uuid.uuid4(),
            "timestamput": datetime.datetime.utcnow(),
            "root": device_status,
        }
        status = {"root": c_status}
        xml_format = xmltodict.unparse(status, pretty=True)

        # print("/topic/" + self.config["outgoing_topic"])

        self.conn.send(
            body=xml_format,
            destination="/topic/" + self.config["outgoing_topic"],
        )

    def connect_to_cooler(self):
        """Connect to the cooler

        Connect to the CCD cooler control.
        """
        # List out the devices available from the INDI server
        devlist = [d.getDeviceName() for d in self.indiclient.getDevices()]
        print(f"This is the list of connected devices: {devlist}")

        # Check that the desired CCD is in the list of devices on the INDI server
        self.cooler = self.config["cooler_name"]
        if self.cooler not in devlist:
            print(f"Warning: {self.cooler} not in the list of available INDI devices!")
            return

        # Get the device from the INDI server
        device_cooler = self.indiclient.getDevice(self.cooler)
        while not device_cooler:
            print("  Waiting on connection to the CMOS Camera...")
            time.sleep(0.5)
            device_cooler = self.indiclient.getDevice(self.cooler)
        self.device_cooler = device_cooler

        # Make the connection -- exit if no connection
        cooler_connect = self.device_cooler.getSwitch("CONNECTION")
        while not cooler_connect:
            print("not connected")
            time.sleep(0.5)
            cooler_connect = self.device_cooler.getSwitch("CONNECTION")
        while not self.device_cooler.isConnected():
            print("still not connected")
            cooler_connect[0].s = PyIndi.ISS_ON  # the "CONNECT" switch
            cooler_connect[1].s = PyIndi.ISS_OFF  # the "DISCONNECT" switch
            self.indiclient.sendNewSwitch(cooler_connect)
            time.sleep(0.5)
        # print(f"Are we connected yet? {self.device_cooler.isConnected()}")
        if not self.device_cooler.isConnected():
            sys.exit()

        # Print a happy acknowledgment
        print(f"The Agent is now connected to {self.cooler}")

    def disconnect_from_cooler(self):
        """Disconnect from the cooler

        _extended_summary_
        """
        # Turn off cooler
        cooler_power = self.device_cooler.getSwitch("CCD_COOLER")
        cooler_power[0].s = PyIndi.ISS_OFF  # the "COOLER_ON" switch
        cooler_power[1].s = PyIndi.ISS_ON  # the "COOLER_OFF" switch
        self.indiclient.sendNewSwitch(cooler_power)

        # Reset instance attributes
        self.cooler = None
        self.device_cooler = None

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
        temp = self.device_cooler.getNumber("CCD_TEMPERATURE")
        temp[0].value = float(cool_temp)  ### new temperature to reach
        self.indiclient.sendNewNumber(temp)

        # NOTE: This should probably also send a "Wait" command back to the DTO
        #       and should quietly loop until either the temperature reaches
        #       the requested value or a timeout is reached.
        self.conn.send(
            body="WAIT", destination="/topic/" + self.config["dto_command_topic"]
        )

        ccd_cooler_temp = self.device_status["CCD_TEMPERATURE"]["vals"][0][1]
        ccd_cooler_powr = self.device_status["CCD_COOLER_POWER"]["vals"][0][1]
        ccd_cooler_ramp = self.device_status["CCD_TEMP_RAMP"]["vals"][0][1]

        print(
            f"Temperature difference: {np.abs(ccd_cooler_temp - cool_temp):.1f}Cº  "
            f"Temperature ramp {ccd_cooler_ramp:.3f}Cº/min  "
            f"Tolerance: {tolerance:.1f}Cº   "
            f"Stable condition: {np.abs(ccd_cooler_temp - cool_temp) <= tolerance}"
        )

        while np.abs(ccd_cooler_temp - cool_temp) > tolerance:
            temp = self.device_cooler.getNumber("CCD_TEMPERATURE")
            temp[0].value = float(cool_temp)  ### new temperature to reach
            self.indiclient.sendNewNumber(temp)

            time.sleep(0.5)
            # Broadcast the status while we're waiting
            self.get_status_and_broadcast()

            ccd_cooler_temp = self.device_status["CCD_TEMPERATURE"]["vals"][0][1]
            ccd_cooler_powr = self.device_status["CCD_COOLER_POWER"]["vals"][0][1]
            ccd_cooler_ramp = self.device_status["CCD_TEMP_RAMP"]["vals"][0][1]
            print(
                f"CCD Temp: {ccd_cooler_temp:.1f}ºC  "
                f"Set point: {cool_temp:.1f}ºC  "
                f"Cooler Ramp: {ccd_cooler_ramp:.3f}Cº/min  "
                f"Cooler Power: {ccd_cooler_powr:.0f}%"
            )
        print(
            f"Cooler is stable at {ccd_cooler_temp:.1f}ºC, cooler power: {ccd_cooler_powr:.0f}%"
        )
        self.conn.send(
            body="GO", destination="/topic/" + self.config["dto_command_topic"]
        )
