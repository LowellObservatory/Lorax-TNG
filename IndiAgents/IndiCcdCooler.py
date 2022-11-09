# -*- coding: utf-8 -*-
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
#  Created on 21-Oct-2022
#
#  @author: dlytle, tbowers

"""Lorax CcdCooler Agent for INDI-based CCD and CMOS cameras

This module is part of the Lorax-TNG package, written at Lowell Observatory.

This CCD Cooler Agent concerns itself with the cooler aspects of the INDI
device.  This agent is called from the CompositeAgent class by instruction from
the instrument-specific configuration file.

Hardware control of the thermoelectric cooler is accomplished through an INDI
interface, contained in the IndiClient module.
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
from AbstractAgents.CcdCoolerSubAgent import CcdCoolerSubAgent
from IndiAgents.IndiClient import IndiClient


class IndiCcdCooler(CcdCoolerSubAgent):
    """INDI CCD Cooler Agent (SubAgent to CompositeAgent)

    This class handles all of the hardware-specific portions of the
    CcdCoolerAgent implementation, leaving the more general, generic methods
    for the abstract parent class.

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
        print(
            f"   ---> Initializing the INDI Camera SubAgent for {config['cooler_name']}"
        )
        super().__init__(logger, conn, config)
        # Get the host and port for the connection to cooler.
        # "config", in this case, is just a dictionary.
        self.indiclient = IndiClient(self, config)
        # print(self.config)
        self.indiclient.setServer(
            self.config["cooler_host"], self.config["cooler_port"]
        )
        self.device_status = {}

        self.indiclient.connectServer()

        # Make the connection to the specified device
        device_cooler = self.indiclient.getDevice(self.config["cooler_name"])
        while not device_cooler:
            time.sleep(0.5)
            device_cooler = self.indiclient.getDevice(self.config["cooler_name"])

        self.device_cooler = device_cooler

        # Define other instance attributes for later population
        self.cooler = None

    def get_status_and_broadcast(self):
        """Get the current status and broadcast it

        _extended_summary_
        """
        # Check if the cooler is connected
        device_status = self.device_status if self.device_cooler.isConnected() else {}

        c_status = {
            "message_id": uuid.uuid4(),
            "timestamput": datetime.datetime.utcnow(),
            "root": device_status,
        }
        for key in self.device_status:
            c_status[key] = self.device_status[key]

        status = {"ccdcooler": c_status}
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
            print("  Waiting on connection to the cooler...")
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
        self.power_off()
        # Reset parameters
        self.reset_parameters()

    def set_temperature(self, cool_temp, tolerance=1.0):
        """Set the cooler temperature

        Set the temperature goal of the cooler, which also turns on the cooler
        power.

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
        print(f"Setting Cooler Temperature to {cool_temp:.1f}ºC")

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

        print(f"Device Status Keys: {list(self.device_status.keys())}")
        print(f"Device Status: {self.device_status}")

        ccd_cooler_temp = self.device_status["CCD_TEMPERATURE_VALUE"]
        ccd_cooler_powr = self.device_status["CCD_COOLER_VALUE"]
        ccd_cooler_ramp = self.device_status["RAMP_SLOPE"]

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

            ccd_cooler_temp = self.device_status["CCD_TEMPERATURE_VALUE"]
            ccd_cooler_powr = self.device_status["CCD_COOLER_VALUE"]
            ccd_cooler_ramp = self.device_status["RAMP_SLOPE"]
            print(
                f"CCD Temp: {ccd_cooler_temp:.1f}ºC  "
                f"Set point: {cool_temp:.1f}ºC  "
                f"Cooler Ramp: {ccd_cooler_ramp:.3f}Cº/min  "
                f"Cooler State: {'ON' if self.device_status['COOLER_ON'] else 'OFF'}  "
                f"Cooler Power: {ccd_cooler_powr:.0f}%"
            )
        print(
            f"Cooler is stable at {ccd_cooler_temp:.1f}ºC, cooler power: {ccd_cooler_powr:.0f}%"
        )
        self.conn.send(
            body="GO", destination="/topic/" + self.config["dto_command_topic"]
        )

    def power_off(self):
        """Turn the cooler power off

        _extended_summary_
        """
        cooler_power = self.device_cooler.getSwitch("CCD_COOLER")
        cooler_power[0].s = PyIndi.ISS_OFF  # the "COOLER_ON" switch
        cooler_power[1].s = PyIndi.ISS_ON  # the "COOLER_OFF" switch
        self.indiclient.sendNewSwitch(cooler_power)
        print("INDI CCD Cooler: Power switched off")

    def reset_parameters():
        pass
