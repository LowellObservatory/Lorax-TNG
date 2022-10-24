import PyIndi
from SubAgent import SubAgent
import time
import uuid
import xmltodict
from datetime import datetime, timezone
import numpy as np


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
        device_name = p.getDeviceName()
        if "CCD" in device_name:
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
        pass
        # prop_name = tvp.name
        # prop_type = 2
        # # Text type
        # temp = tvp.getText()
        # prop_dict = {"prop_type": prop_type}
        # prop_dict["length"] = len(temp)
        # prop_vals = []
        # for val in temp:
        #     prop_vals.append((val.name, val.text))
        # prop_dict["vals"] = prop_vals
        # self.parent.device_status[prop_name] = prop_dict

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


class SBIGCcdCooler(SubAgent):
    def __init__(self, logger, conn, config):
        print("in SBIGCcdCooler.init")
        SubAgent.__init__(self, logger, conn, config)
        # Get the host and port for the connection to mount.
        # "config", in this case, is just a dictionary.
        self.indiclient = IndiClient(self)
        # print(self.config)
        self.indiclient.setServer(
            self.config["cooler_host"], self.config["cooler_port"]
        )
        self.device_status = {}

        self.indiclient.connectServer()

        device_ccd = self.indiclient.getDevice(self.config["cooler_name"])
        while not (device_ccd):
            time.sleep(0.5)
            device_ccd = self.indiclient.getDevice(self.config["cooler_name"])

        self.device_ccd = device_ccd

    def get_status_and_broadcast(self):

        # print(self.device_status)

        c_status = {
            "message_id": uuid.uuid4(),
            "timestamput": datetime.now(timezone.utc),
            "root": self.device_status,
        }
        status = {"root": c_status}
        xml_format = xmltodict.unparse(status, pretty=True)

        print("/topic/" + self.config["outgoing_topic"])

        self.conn.send(
            body=xml_format,
            destination="/topic/" + self.config["outgoing_topic"],
        )

    def handle_message(self, message):
        print("got message: in SBIGCcdCooler")
        print(message)

        if "(" in message:
            mcom = message[0 : message.find("(")]
        else:
            mcom = message
        print(mcom)

        if mcom == "settemp":
            # Get the arguments.
            # setTemp(-45.0)
            print("doing settemp")
            com = message
            temperature = float(com[com.find("(") + 1 : com.find(")")])
            print("setting temp to " + str(temperature))
            temp = self.device_ccd.getNumber("CCD_TEMPERATURE")
            temp[0].value = np.float(temperature)  ### new temperature to reach
            self.indiclient.sendNewNumber(temp)

        elif mcom == "status":
            print("doing status")
            self.get_status_and_broadcast()

        # if "set_temp" in message:
        # send set temp.
        # send "wait" to DTO.
        # send specific command, "set temp", to ccd cooler
        # keep checking status until temp within limits.
        # send "go" command to DTO.
        # print("ccd cooler: set temp")
        # if "report_temp" in message:
        # report temp.
        # send specific command, "report temp", to ccd cooler
        # broadcast temp
        # print("ccd cooler: report temp")

        else:
            print("Unknown command")
