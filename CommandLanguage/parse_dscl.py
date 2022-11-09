# -*- coding: utf-8 -*-
#
#  This Source Code Form is subject to the terms of the Mozilla Public
#  License, v. 2.0. If a copy of the MPL was not distributed with this
#  file, You can obtain one at http://mozilla.org/MPL/2.0/.
#
#  Created on 08-Nov-2022
#
#  @author: dlytle, tbowers

"""Lorax Command Language Parser for Dyer's Simple Command Language

This module is part of the Lorax-TNG package, written at Lowell Observatory.

Parser module for Dyer's Simple Command Language

"""
# Built-In Libraries

# 3rd Party Libraries

# Internal Imports


def parse_command(command: str) -> tuple:
    """VERY Simple-Minded Command Parsing

    I am QUITE sure there is a better way to do this, but brute force does get
    the job done.

    Parameters
    ----------
    command : str
        The command sent from the DTO in "Dyer's Simple Command Language"

    Returns
    -------
    command : str
        The actual command sent (minus any arguments)
    arguments : list
        Arguments, if any, of the command (`e.g.`, ``settemp(-12.0)``)
    """
    # Strip all whitespace from ends of the string; set arguments to list of None
    command = command.strip()
    arguments = [None]

    # Parse any arguments to the command
    if "(" in command:
        args = command[command.find("(") + 1 : command.find(")")]

        # Get the command without the arguments
        command = command.removesuffix(f"({args})")

        # Split up the arguments into a list
        arguments = args.split(",")

        # Try to convert things to float... leave them be if ValueError
        for i, arg in enumerate(arguments):
            try:
                arguments[i] = float(arg)
            except ValueError:
                # Try stripping off any quotes
                arguments[i] = arg.strip("'").strip('"')

    return (command, arguments)


# =============================================================================#
# For command-line testing
if __name__ == "__main__":

    print(parse_command("  expose"))
    print(parse_command(" waituntil('time', 1:30)"))
    print(parse_command("  set_temperature(-10)"))
    print(parse_command(" gotoAltAz(45.6, 170.34)"))
    print(parse_command(" end"))
