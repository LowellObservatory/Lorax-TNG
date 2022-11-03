# -*- coding: utf-8 -*-
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
#  Created on 21-Oct-2022
#
#  @author: dlytle, tbowers

"""Lorax Composite Agent Driver

This module is part of the Lorax-TNG package, written at Lowell Observatory.

This Composite Agent Driver handles control for all of the components of a
Lorax "Thing", as defined in the passed-in configuration file.  The particular
comminication-protocol-based Agents can be mixed and matched for a particular
instrument or application, and the CompositeAgent class instantiates the ones
defined in the config file.
"""

# Built-In Libraries
import argparse
import sys
import time

# 3rd Party Libraries

# Internal Imports
from CompositeAgent import CompositeAgent


def main():

    # Parse Arguments
    parser = argparse.ArgumentParser("run_CompositeAgent")
    parser.add_argument("conffile", type=str, help="Configuration file for Agent")
    args = parser.parse_args()

    # Run the Agent
    print(" in main ")
    composite_agent = CompositeAgent(args.conffile)
    print("   ===> Agent Initialized... waiting on commands")
    while True:
        if composite_agent.message_received:
            composite_agent.handle_message()
            composite_agent.message_received = 0
        else:
            composite_agent.get_status_and_broadcast()
        time.sleep(composite_agent.config["message_wait_time"])


if __name__ == "__main__":
    # Giddy up!
    sys.exit(main())
