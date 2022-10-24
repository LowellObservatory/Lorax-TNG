import PyIndi
from SubAgent import SubAgent
import time
import sys
import astropy.io.fits
import io
import threading
from datetime import datetime


class IndiClient(PyIndi.BaseClient):
    def __init__(self, parent):
        super(IndiClient, self).__init__()
        self.parent = parent
        self.blobEvent = threading.Event()
        self.camera = None
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
        # prop_name = p.getName()
        device_name = p.getDeviceName()
        if "CCD" in device_name:
            print("storing prop: " + p.getName())
            self.store_prop(p)

    def removeProperty(self, p):
        pass

    def newBLOB(self, bp):
        print("new BLOB ", bp.name)
        self.blobEvent.set()

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
        self.exptime = 1.0
        self.exptype = "FRAME_LIGHT"
        self.ccd_binning = (1, 1)
        # -----

    def get_status_and_broadcast(self):
        # current_status = self.status()
        # print("Status: " + current_status)
        print("camera status")

    def handle_message(self, message):
        print("got message: in SBIGCamera")
        print(message)
        if "init" in message:
            # List out the devices available from the INDI server
            devlist = [d.getDeviceName() for d in self.indiclient.getDevices()]
            print(f"This is the list of connected devices: {devlist}")

            # Check that the desired CCD is in the list of devices on the INDI server
            self.ccd = self.config["camera_name"]
            if self.ccd not in devlist:
                print(f"Warning: {self.ccd} not in the list of available INDI devices!")
                return

            # Get the device from the INDI server
            device_ccd = self.indiclient.getDevice(self.ccd)
            while not device_ccd:
                print("  Waiting on connection to the CCD Camera...")
                time.sleep(0.5)
                device_ccd = self.indiclient.getDevice(self.ccd)
            self.device_ccd = device_ccd

            # Make the connection -- exit if no connection
            ccd_connect = self.device_ccd.getSwitch("CONNECTION")
            while not ccd_connect:
                print("not connected")
                time.sleep(0.5)
                ccd_connect = self.device_ccd.getSwitch("CONNECTION")
            while not device_ccd.isConnected():
                print("still not connected")
                ccd_connect[0].s = PyIndi.ISS_ON  # the "CONNECT" switch
                ccd_connect[1].s = PyIndi.ISS_OFF  # the "DISCONNECT" switch
                self.indiclient.sendNewSwitch(ccd_connect)
                time.sleep(0.5)
            print(f"Are we connected yet? {self.device_ccd.isConnected()}")
            if not self.device_ccd.isConnected():
                pass

            # Print a happy acknowledgment
            print(f"The Agent is now connected to {self.ccd}")

            # Tell the INDI server send the "CCD1" blob to this client
            self.indiclient.setBLOBMode(PyIndi.B_ALSO, self.ccd, "CCD1")

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
            # ---------------------
            #  """CameraAgent: Take an exposure
            # This method takes an exposure with the camera.  The various settings
            # need to have been adjusted before this command is executed.  If any of
            # the required settings are ``None``, this method will emmit a warning
            # and return without exposing.
            # NOTE: An exposure is triggered when the exposure number vector property
            #   is sent to the camera via the INDI server, like::
            #     self.indiclient.sendNewNumber(ccd_exposure)
            # Parameters
            # ----------
            # n_exp : ``int``
            # Number of exposures to be taken.  (Default: 1)
            # """
            # if not self.check_camera_connection():
            #     return
            # print("QHY600 Expose...")

            # Check the required exposure properties
            if not self.exptime:
                print("WARNING: Must specify exposure time before exposing!")
                return
            if not self.exptype:
                print("WARNING: Must specify exposure type before exposing!")
                return

            # Say what we're going to do
            print(f"Exposing {self.exptype} frame for {self.exptime:.2f}s...")

            while not (ccd_active_devices := self.device_ccd.getText("ACTIVE_DEVICES")):
                time.sleep(0.5)
            ccd_active_devices[0].text = "Telescope Simulator"
            self.indiclient.sendNewText(ccd_active_devices)

            # Retrieve the CCD_EXPOSURE number vector property from the camera
            print("getting ccd_exposure")
            while not (ccd_exposure := self.device_ccd.getNumber("CCD_EXPOSURE")):
                print(ccd_exposure)
                time.sleep(0.5)
            print("got ccdexposure")
            # print(ccd_exposure)

            # Retrieve the CCD1 vector blob property from the camera
            while not (ccd_ccd1 := self.device_ccd.getBLOB("CCD1")):
                time.sleep(0.5)
                sys.stderr.write(".")
            print(f"Got BLOB CCD1 from {self.ccd}")
            # -------------------------
            # Set up the list of desired exposure time(s) (just one for now)
            # exposures = [self.exptime for _ in range(1)]

            # Set up threading so that the next exposure can begin while the
            #   present one is being processed
            self.indiclient.blobEvent.clear()

            # Set the ccd_exposure value and send it to
            #   the camera to begin taking the exposure.
            ccd_exposure[0].value = 10.0
            self.indiclient.sendNewNumber(ccd_exposure)

            self.indiclient.blobEvent.wait()

            # Meanwhile, process the received exposure
            for blob in ccd_ccd1:
                # Print out some information about this exposure
                print(f"name: {blob.name} size: {blob.size} format: {blob.format}")

                # Use the PyIndi-supplied getblobdata() method to access the contents of
                #   the BLOB, which is a bytearray in Python.  Run it through io.BytesIO
                #   and AstroPy to produce a fully functional FITS HDUList.
                hdulist = astropy.io.fits.open(io.BytesIO(blob.getblobdata()))

                # Write to disk
                # TODO: Here is where we'd add the Locutus-supplied FITS header information
                #       Also, figure out how to do some sort of incremental file numbering
                #       or something.
                hdulist.writeto("simimage.fits", overwrite=True)
            # ---------------------

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
