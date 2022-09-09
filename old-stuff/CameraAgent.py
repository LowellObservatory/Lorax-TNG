from Agent import Agent
from abc import ABC, abstractmethod


class CameraAgent(Agent):
    def __init__(self, cfile):
        print("in CameraAgent.init")
        super().__init__(cfile)

    def get_status_and_broadcast(self):
        current_status = self.status()
        if current_status:
            print(f"Status: {current_status}")

    def handle_message(self):
        print("(camera) message: ", end="")
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
            pass
        if "set_exposure_length" in msg:
            # check arguments against exposure length limits.
            # send camera specific set_exposure_length.
            try:
                exptime = float(msg[msg.find("(") + 1 : msg.find(")")])
            except ValueError:
                print("Exposure time must be a float.")
                return
            self.set_exposure_length(exptime)

        if "set_exposure_type" in msg:
            # check arguments against exposure types.
            # send camera specific set_exposure_type.
            try:
                exptype = str(msg[msg.find("(") + 1 : msg.find(")")])
            except ValueError:
                print("Exposure type must be a str.")
                return
            self.set_exposure_type(exptype)

        if "set_binning" in msg:
            # check arguments against binning limits.
            # send camera specific set_binning.
            pass
        if "set_origin" in msg:
            # check arguments against origin limits.
            # send camera specific set_origin.
            pass
        if "set_size" in msg:
            # check arguments against size limits.
            # send camera specific set_size.
            pass
        if "connect_to_camera" in msg:
            # check arguments.
            # do whatever is necessary to connect to the camera
            self.connect_to_camera()

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

    @abstractmethod
    def connect_to_camera(self):
        pass
