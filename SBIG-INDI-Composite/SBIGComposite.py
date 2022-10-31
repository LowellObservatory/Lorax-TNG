# Built-In Libraries
import inspect
import os
import sys
import time

# 3rd Party Libraries

# Internal Imports
from AbstractAgents.CompositeAgent import CompositeAgent

currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0, parentdir)



class SBIGComposite(CompositeAgent):
    def __init__(self, config_file):
        CompositeAgent.__init__(self, config_file)
        print("in SBIGComposite.init")

    def get_status_and_broadcast(self):
        # Send "get_status_and_broadcast" to each of the sub_agents.
        for agent in self.agents:
            agent.get_status_and_broadcast()
        time.sleep(self.config["message_wait_time"])


if __name__ == "__main__":
    print(" in main ")
    SBIG_comp = SBIGComposite("SBIG-INDI-Composite/SBIG_composite_config.yaml")
    print(" in main after instantiate ")
    while True:
        if SBIG_comp.message_received:
            SBIG_comp.handle_message()
            SBIG_comp.message_received = 0
        else:
            SBIG_comp.get_status_and_broadcast()
        time.sleep(SBIG_comp.config["message_wait_time"])
