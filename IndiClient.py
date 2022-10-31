import PyIndi
import threading


class IndiClient(PyIndi.BaseClient):
    def __init__(self, parent, config):
        super(IndiClient, self).__init__()
        self.parent = parent
        self.config = config
        self.blobEvent = threading.Event()
        self.camera = None

    def newDevice(self, d):
        print("Receiving Device... " + d.getDeviceName())
        self.device = d
        self.parent.device = d

    def newProperty(self, p):
        # print(dir(p))
        # print("new property " + p.getName() + " for device " + p.getDeviceName())
        prop_name = p.getName()
        if prop_name in self.config["status"]:
            print("storing prop: " + p.getName())
            self.store_prop(p)

    def removeProperty(self, p):
        pass

    def newBLOB(self, bp):
        print("new BLOB ", bp.name)
        self.blobEvent.set()

    def newSwitch(self, svp):
        prop_name = svp.name
        if prop_name in self.config["status"]:
            for val in svp:
                self.parent.device_status[val.name] = val.s
            self.parent.get_status_and_broadcast()

    def newNumber(self, nvp):
        prop_name = nvp.name
        if prop_name in self.config["status"]:
            for val in nvp:
                self.parent.device_status[val.name] = val.value
            self.parent.get_status_and_broadcast()

    def newText(self, tvp):
        prop_name = tvp.name
        if prop_name in self.config["status"]:
            for val in tvp:
                self.parent.device_status[val.name] = val.text
            self.parent.get_status_and_broadcast()

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
        print(prop_name)
        prop_type = prop.getType()
        if prop_name in self.config["status"]:
            if prop_type == 0:
                # Number Type
                temp = prop.getNumber()
                for val in temp:
                    # if val.name in self.config["status"]:
                    self.parent.device_status[val.name] = val.value

            elif prop_type == 1:
                # Switch type
                temp = prop.getSwitch()
                for val in temp:
                    # if val.name in self.config["status"]:
                    self.parent.device_status[val.name] = val.s

            elif prop_type == 2:
                # Text type
                temp = prop.getText()
                for val in temp:
                    # if val.name in self.config["status"]:
                    self.parent.device_status[val.name] = val.text

            elif prop_type == 3:
                # Light type
                temp = prop.getLight()
                for val in temp:
                    # if val.name in self.config["status"]:
                    self.parent.device_status[val.name] = val.text
