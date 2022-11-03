-----
This directory will contain INDI hardware-specific Agents and communication
protocol clients.

The modules herein should be general to ALL INDI hardware, and build upon
AbstractAgents for the more general aspects of the needed Agents.

Currently, the contents are:
    * IndiClient.py -- Contains the INDI communication protocols
    * IndiCamera.py -- CameraAgent for communication with an INDI CCD camera
    * IndiCcdCooler.py -- CcdCoolerAgent for communication with an INDI cooler

TPEB, 11/3/22
