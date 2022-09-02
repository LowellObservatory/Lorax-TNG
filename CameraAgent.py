from Agent import Agent
from abc import ABC, abstractmethod


class CameraAgent(Agent):
    def __init__(self, cfile):
        print("in CameraAgent.init")
        Agent.__init__(self, cfile)

    def get_status_and_broadcast(self):
        current_status = self.status()
        print("Status: " + current_status)

    def handle_message(self):
        print("message: ", end="")
        print(self.current_message.headers["destination"] + ": ", end="")
        print(self.current_message.body)

    @abstractmethod
    def status(self):
        pass

    @abstractmethod
    def expose(self):
        pass

    @abstractmethod
    def set_exposure_length(self, exposure_length):
        pass

    @abstractmethod
    def set_exposure_type(self, exposure_type):
        pass

    @abstractmethod
    def set_binning(self, x_binning, y_binning):
        pass

    @abstractmethod
    def set_origin(self, x, y):
        pass

    @abstractmethod
    def set_size(self, width, height):
        pass
