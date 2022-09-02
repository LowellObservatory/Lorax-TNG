from Agent import Agent
import time
from datetime import datetime


class TestAgent(Agent):
    def __init__(self, cfile):
        print("in TestAgent.init")
        Agent.__init__(self, cfile)

    def get_status_and_broadcast(self):
        now = datetime.now()
        print(
            "Broadcasting Status! " + now.strftime("%d/%m/%Y %H:%M:%S") + "\r", end=""
        )

    def handle_message(self):
        print("")
        print("message: ", end="")
        print(self.current_message.headers["destination"] + ": ", end="")
        print(ta.current_message.body)


if __name__ == "__main__":
    ta = TestAgent("AgentConfig.yaml")

    while True:
        if ta.message_received:
            ta.handle_message()
            ta.message_received = 0
        else:
            ta.get_status_and_broadcast()
        time.sleep(ta.config["status_broadcast_rate"])
