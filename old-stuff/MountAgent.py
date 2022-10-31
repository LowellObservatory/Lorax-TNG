from Agent import Agent
from abc import ABC, abstractmethod


class MountAgent(Agent):
    def __init__(self, cfile):
        print("in MountAgent.init")
        Agent.__init__(self, cfile)

    def get_status_and_broadcast(self):
        current_status = self.status()
        print("Status: " + current_status)

    def handle_message(self):
        print("message: ", end="")
        print(self.current_message.headers["destination"] + ": ", end="")
        print(self.current_message.body)
        msg = self.current_message.body
        # if "connect" in msg:
        #     pass
