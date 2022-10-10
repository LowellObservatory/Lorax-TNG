from SubAgent import SubAgent
import time
from datetime import datetime


class SBIGCcdCooler(SubAgent):
    def __init__(self, logger, conn, config):
        print("in SBIGCcdCooler.init")
        SubAgent.__init__(self, logger, conn, config)

    def get_status_and_broadcast(self):
        # current_status = self.status()
        # print("Status: " + current_status)
        print("ccd cooler status")

    def handle_message(self):
        print("got message: in SBIGCcdCooler")
        print(self.current_destination)
        print(self.current_message)
        if "set_temp" in self.current_message:
            # send set temp.
            # send "wait" to DTO.
            # send specific command, "set temp", to ccd cooler
            # keep checking status until temp within limits.
            # send "go" command to DTO.
            print("ccd cooler: set temp")
        if "report_temp" in self.current_message:
            # report temp.
            # send specific command, "report temp", to ccd cooler
            # broadcast temp
            print("ccd cooler: report temp")
