from Agent import Agent
from abc import ABC, abstractmethod


class CoolerAgent(Agent):
    def __init__(self, cfile):
        print("in CoolerAgent.init")
        super().__init__(cfile)

    def get_status_and_broadcast(self):
        current_status = self.status()
        if current_status:
            print(f"Status: {current_status}")

    def handle_message(self):
        print("(cooler) message: ", end="")
        print(self.current_message.headers["destination"] + ": ", end="")
        print(self.current_message.body)
        msg = self.current_message.body
        if "expose" in msg:
            # check arguments.
            # check exposure settings.
            # send "wait" to DTO.
            # request FITS dictionary from Locutus.
            # send camera specific command to camera. (call cam_specific_expose)
            # when done, request another FITS dictionary from Locutus.
            # save image data to local disk.
            # spawn fits_writer in seperate process (data, fits1, fits2)
            # send "go" command to DTO.
            self.expose()

        if "set_temperature" in msg:
            # check arguments against temperature limits.
            # send cooler specific set_temperature.
            try:
                cool_temp = float(msg[msg.find("(") + 1 : msg.find(")")])
            except ValueError:
                print("Cooler temperature must be a float.")
                return
            self.set_temperature(cool_temp)

        if "connect_to_cooler" in msg:
            # check arguments.
            # do whatever is necessary to connect to the camera
            self.connect_to_cooler()

    @abstractmethod
    def status(self):
        pass

    @abstractmethod
    def set_temperature(self, cool_temp):
        pass

    @abstractmethod
    def connect_to_cooler(self):
        pass
