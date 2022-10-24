# -*- coding: utf-8 -*-
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
#  Created on 21-Oct-2022
#
#  @author: dlytle, tbowers

"""Lorax Composite Agent for the QHY 600M CMOS Camera

This module is part of the Lorax-TNG package, written at Lowell Observatory.

This Composite Agent handles control for all of the components of the QHY 600M
CMOS camera.  It calls submodules QHY600Camera and QHY600CcdCooler, and could
also call a future QHY600FilterWheel, if needed.

Hardware control of the QHY 600M is accomplished through an INDI interface,
contained in the HardwareClients module.
"""

# Built-In Libraries
import time

# 3rd Party Libraries

# Internal Imports
from CompositeAgent import CompositeAgent


class QHY600Composite(CompositeAgent):
    """QHY600M Composite Agent

    _extended_summary_

    Parameters
    ----------
    config_file : :obj:`str` or :obj:`pathlib.Path`
        Name of or path to the configuration file for this Agent
    """

    def __init__(self, config_file):
        super().__init__(config_file)
        print("in QHY600Composite.init")

    # def get_status_and_broadcast(self):
    #     # Send "get_status_and_broadcast" to each of the sub_agents.
    #     for agent in self.agents:
    #         agent.get_status_and_broadcast()
    #     # time.sleep(self.config["message_wait_time"])


# =============================================================================#
# Command line interface

if __name__ == "__main__":
    print(" in main ")
    QHY600_comp = QHY600Composite("qhy600_agent.yaml")
    print(" in main after instantiate ")
    while True:
        if QHY600_comp.message_received:
            QHY600_comp.handle_message()
            QHY600_comp.message_received = 0
        else:
            QHY600_comp.get_status_and_broadcast()
        time.sleep(QHY600_comp.config["message_wait_time"])
