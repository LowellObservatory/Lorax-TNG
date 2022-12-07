# Built-In Libraries
import inspect
import os
import sys
import time

# 3rd Party Libraries

# Internal Imports
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)
from CompositeAgent import CompositeAgent


class PWMountComposite(CompositeAgent):
    """PWMount Composite Agent

    _extended_summary_

    Parameters
    ----------
    config_file : _type_
        _description_
    """

    def __init__(self, config_file):
        CompositeAgent.__init__(self, config_file)
        print("in PWMountComposite.init")

    def get_status_and_broadcast(self):
        # Send "get_status_and_broadcast" to each of the sub_agents.
        for agent in self.agents:
            agent.get_status_and_broadcast()
        time.sleep(self.config["message_wait_time"])


if __name__ == "__main__":
    print(" in main ")
    PWMount_comp = PWMountComposite("PWMount_Agent/PWMountConfig.yaml")
    print(" in main after instantiate ")
    while True:
        if PWMount_comp.message_received:
            PWMount_comp.handle_message()
            PWMount_comp.message_received = 0
        else:
            PWMount_comp.get_status_and_broadcast()
        time.sleep(PWMount_comp.config["message_wait_time"])
