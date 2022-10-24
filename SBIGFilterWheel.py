from SubAgent import SubAgent
import time
from datetime import datetime


class SBIGFilterWheel(SubAgent):
    def __init__(self, logger, conn, config):
        print("in SBIGFilterWheel.init")
        SubAgent.__init__(self, logger, conn, config)

    def get_status_and_broadcast(self):
        # current_status = self.status()
        # print("Status: " + current_status)
        print("filter wheel status")

    def handle_message(self, message):
        print("got message: in SBIGFilterWheel")
        print(message)
        if "home" in message:
            # send wheel home.
            # send "wait" to DTO.
            # send specific command, "home", to filter wheel
            # keep checking status until done.
            # send "go" command to DTO.
            print("filter wheel: home")
        if "move" in message:
            # send wheel to specific position.
            # check arguments against position limits.
            # send "wait" to DTO.
            # send specific command, "movoto x", to filter wheel
            # keep checking status until done.
            # send "go" command to DTO.
            print("filter wheel: move")