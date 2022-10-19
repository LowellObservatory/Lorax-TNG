import PyIndi
from SubAgent import SubAgent
import time
from datetime import datetime


class IndiClient(PyIndi.BaseClient):
    def __init__(self, parent):
        super(IndiClient, self).__init__()
        self.parent = parent
        status = {}

    def newDevice(self, d):
        print("Receiving Device... " + d.getDeviceName())
        self.device = d
        self.parent.device = d

    def newProperty(self, p):
        # print(dir(p))
        # print("new property " + p.getName() + " for device " + p.getDeviceName())
        # print("type = " + str(p.getType()))
        # Go store the property in the appropriate status dictionary.
        prop_name = p.getName()
        if "CCD" in prop_name or "FILTER" in prop_name:
            self.store_prop(p)

    def removeProperty(self, p):
        pass

    def newBLOB(self, bp):
        global blobEvent
        print("new BLOB ", bp.name)
        blobEvent.set()
        pass

    def newSwitch(self, svp):
        prop_name = svp.name
        prop_type = 1
        prop_dict = {"prop_type": prop_type}
        prop_dict["length"] = len(svp)
        prop_vals = []
        for val in svp:
            prop_vals.append((val.name, val.s))
        prop_dict["vals"] = prop_vals
        self.parent.device_status[prop_name] = prop_dict

    def newNumber(self, nvp):
        prop_name = nvp.name
        prop_type = 0
        prop_dict = {"prop_type": prop_type}
        prop_dict["length"] = len(nvp)
        prop_vals = []
        for val in nvp:
            prop_vals.append((val.name, val.value))
        prop_dict["vals"] = prop_vals
        self.parent.device_status[prop_name] = prop_dict

    def newText(self, tvp):
        prop_name = tvp.name
        prop_type = 2
        # Text type
        temp = tvp.getText()
        prop_dict = {"prop_type": prop_type}
        prop_dict["length"] = len(temp)
        prop_vals = []
        for val in temp:
            prop_vals.append((val.name, val.text))
        prop_dict["vals"] = prop_vals
        self.parent.device_status[prop_name] = prop_dict

    def newLight(self, lvp):
        pass

    def newMessage(self, d, m):
        pass

    def serverConnected(self):
        pass

    def serverDisconnected(self, code):
        pass

    def store_prop(self, prop):
        prop_name = prop.getName()
        prop_type = prop.getType()

        if not prop_name in self.parent.device_status:
            if prop_type == 0:
                # Number Type
                temp = prop.getNumber()
                prop_dict = {"prop_type": prop_type}
                prop_dict["length"] = len(temp)
                prop_vals = []
                for val in temp:
                    # print(dir(val))
                    prop_vals.append((val.name, val.value))
                prop_dict["vals"] = prop_vals
                self.parent.device_status[prop_name] = prop_dict
            elif prop_type == 1:
                # Switch type
                temp = prop.getSwitch()
                prop_dict = {"prop_type": prop_type}
                prop_dict["length"] = len(temp)
                prop_vals = []
                for val in temp:
                    # print(dir(val))
                    prop_vals.append((val.name, val.s))
                    # print(val.name)
                prop_dict["vals"] = prop_vals
                self.parent.device_status[prop_name] = prop_dict
            elif prop_type == 2:
                # Text type
                temp = prop.getText()
                # print(len(temp))
                # print(dir(temp[0]))
                prop_dict = {"prop_type": prop_type}
                prop_dict["length"] = len(temp)
                prop_vals = []
                for val in temp:
                    # print(dir(val))
                    prop_vals.append((val.name, val.text))
                # print(val.name)
                prop_dict["vals"] = prop_vals
                self.parent.device_status[prop_name] = prop_dict
                # print(status[prop_name])
            elif prop_type == 3:
                # Light type
                temp = prop.getLight()
                prop_dict = {"prop_type": prop_type}
                prop_dict["length"] = len(temp)
                prop_vals = []
                for val in temp:
                    prop_vals.append((val.name, val.text))
                prop_dict["vals"] = prop_vals
                self.parent.device_status[prop_name] = prop_dict


class SBIGCamera(SubAgent):
    def __init__(self, logger, conn, config):
        print("in SBIGCamera.init")
        SubAgent.__init__(self, logger, conn, config)

        # -----
        # Get the host and port for the connection to mount.
        # "config", in this case, is just a dictionary.
        self.indiclient = IndiClient(self)
        # print(self.config)
        self.indiclient.setServer(
            self.config["camera_host"], self.config["camera_port"]
        )
        self.device_status = {}

        self.indiclient.connectServer()

        device_ccd = self.indiclient.getDevice(self.config["camera_name"])
        while not (device_ccd):
            time.sleep(0.5)
            device_ccd = self.indiclient.getDevice(self.config["camera_name"])

        self.device_ccd = device_ccd
        print(self.device_ccd)
        # -----

    def get_status_and_broadcast(self):
        # current_status = self.status()
        # print("Status: " + current_status)
        print("camera status")

    def handle_message(self, message):
        print("got message: in SBIGCamera")
        print(message)
        if "expose" in message:
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
        if "set_exposure_length" in message:
            # check arguments against exposure length limits.
            # send camera specific set_exposure_length.
            print("camera:set_exposure_length")
        if "set_exposure_type" in message:
            # check arguments against exposure types.
            # send camera specific set_exposure_type.
            print("camera:set_exposure_type")
        if "set_binning" in message:
            # check arguments against binning limits.
            # send camera specific set_binning.
            print("camera:set_binning")
        if "set_origin" in message:
            # check arguments against origin limits.
            # send camera specific set_origin.
            print("camera:set_origin")
        if "set_size" in message:
            # check arguments against size limits.
            # send camera specific set_size.
            print("camera:set_size")
