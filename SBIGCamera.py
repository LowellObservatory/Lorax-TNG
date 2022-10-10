from SubAgent import SubAgent
import time
from datetime import datetime


class SBIGCamera(SubAgent):
    def __init__(self, logger, conn, config):
        print("in SBIGCamera.init")
        SubAgent.__init__(self, logger, conn, config)

    def get_status_and_broadcast(self):
        # current_status = self.status()
        # print("Status: " + current_status)
        print("camera status")

    def handle_message(self):
        print("got message: in SBIGCamera")
        print(self.current_destination)
        print(self.current_message)
        if "expose" in self.current_message:
            # check arguments.
            # check exposure settings.
            # send "wait" to DTO.
            # request FITS dictionary from Locutus.
            # send camera specific command to camera. (call cam_specific_expose)
            # when done, request another FITS dictionary from Locutus.
            # save image data to local disk.
            # spawn fits_writer in seperate process (data, fits1, fits2)
            # send "go" command to DTO.
            print("camera:take exposure")
        if "set_exposure_length" in self.current_message:
            # check arguments against exposure length limits.
            # send camera specific set_exposure_length.
            print("camera:set_exposure_length")
        if "set_exposure_type" in self.current_message:
            # check arguments against exposure types.
            # send camera specific set_exposure_type.
            print("camera:set_exposure_type")
        if "set_binning" in self.current_message:
            # check arguments against binning limits.
            # send camera specific set_binning.
            print("camera:set_binning")
        if "set_origin" in self.current_message:
            # check arguments against origin limits.
            # send camera specific set_origin.
            print("camera:set_origin")
        if "set_size" in self.current_message:
            # check arguments against size limits.
            # send camera specific set_size.
            print("camera:set_size")
