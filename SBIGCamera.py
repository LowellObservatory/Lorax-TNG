import PyIndi
from SubAgent import SubAgent
import time
import sys
import astropy.io.fits
import io
import threading
import uuid
import xmltodict
from datetime import datetime, timezone


class IndiClient(PyIndi.BaseClient):
    def __init__(self, parent, config):
        super(IndiClient, self).__init__()
        self.parent = parent
        self.config = config
        self.blobEvent = threading.Event()
        self.camera = None
        status = {}

    def newDevice(self, d):
        print("Receiving Device... " + d.getDeviceName())
        self.device = d
        self.parent.device = d

    def newProperty(self, p):
        # print(dir(p))
        print("new property " + p.getName() + " for device " + p.getDeviceName())
        # print("type = " + str(p.getType()))
        # Go store the property in the appropriate status dictionary.
        # prop_name = p.getName()
        prop_name = p.getName()
        # print(self.config["status"])
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
        for val in svp:
            if prop_name in self.config["status"]:
                self.parent.device_status[val.name] = val.value
                self.parent.get_status_and_broadcast()

    def newNumber(self, nvp):
        prop_name = nvp.name
        # ----
        for val in nvp:
            if prop_name in self.config["status"]:
                self.parent.device_status[val.name] = val.value
                self.parent.get_status_and_broadcast()

    def newText(self, tvp):
        prop_name = tvp.name
        for val in tvp:
            if prop_name in self.config["status"]:
                self.parent.device_status[val.name] = val.value
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
        prop_type = prop.getType()
        if prop_name in self.config["status"]:
            if not prop_name in self.parent.device_status:
                if prop_type == 0:
                    # Number Type
                    temp = prop.getNumber()
                    for val in temp:
                        if prop_name in self.config["status"]:
                            self.parent.device_status[val.name] = val.value

                elif prop_type == 1:
                    # Switch type
                    temp = prop.getSwitch()
                    for val in temp:
                        if prop_name in self.config["status"]:
                            self.parent.device_status[val.name] = val.s

                elif prop_type == 2:
                    # Text type
                    temp = prop.getText()
                    for val in temp:
                        if prop_name in self.config["status"]:
                            self.parent.device_status[val.name] = val.text

                elif prop_type == 3:
                    # Light type
                    temp = prop.getLight()
                    for val in temp:
                        if prop_name in self.config["status"]:
                            self.parent.device_status[val.name] = val.text


class SBIGCamera(SubAgent):
    def __init__(self, logger, conn, config):
        print("in SBIGCamera.init")
        SubAgent.__init__(self, logger, conn, config)

        # Get the host and port for the connection to mount.
        # "config", in this case, is just a dictionary.
        self.indiclient = IndiClient(self, config)
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
        # connect the scope (apparently we need to do this to get expose to work))
        telescope = "Telescope Simulator"
        device_telescope = None
        telescope_connect = None

        # get the telescope device
        device_telescope = self.indiclient.getDevice(telescope)
        while not (device_telescope):
            time.sleep(0.5)
            device_telescope = self.indiclient.getDevice(telescope)

        # wait CONNECTION property be defined for telescope
        telescope_connect = device_telescope.getSwitch("CONNECTION")
        while not (telescope_connect):
            time.sleep(0.5)
            telescope_connect = device_telescope.getSwitch("CONNECTION")

        # if the telescope device is not connected, we do connect it
        if not (device_telescope.isConnected()):
            # Property vectors are mapped to iterable Python objects
            # Hence we can access each element of the vector using Python indexing
            # each element of the "CONNECTION" vector is a ISwitch
            telescope_connect[0].s = PyIndi.ISS_ON  # the "CONNECT" switch
            telescope_connect[1].s = PyIndi.ISS_OFF  # the "DISCONNECT" switch
            self.indiclient.sendNewSwitch(
                telescope_connect
            )  # send this new value to the device

        # Now let's make a goto to vega
        # Beware that ra/dec are in decimal hours/degrees
        vega = {"ra": (279.23473479 * 24.0) / 360.0, "dec": +38.78368896}

        # We want to set the ON_COORD_SET switch to engage tracking after goto
        # device.getSwitch is a helper to retrieve a property vector
        telescope_on_coord_set = device_telescope.getSwitch("ON_COORD_SET")
        while not (telescope_on_coord_set):
            time.sleep(0.5)
            telescope_on_coord_set = device_telescope.getSwitch("ON_COORD_SET")
        # the order below is defined in the property vector, look at the standard Properties page
        # or enumerate them in the Python shell when you're developing your program
        telescope_on_coord_set[0].s = PyIndi.ISS_ON  # TRACK
        telescope_on_coord_set[1].s = PyIndi.ISS_OFF  # SLEW
        telescope_on_coord_set[2].s = PyIndi.ISS_OFF  # SYNC
        self.indiclient.sendNewSwitch(telescope_on_coord_set)
        # We set the desired coordinates
        telescope_radec = device_telescope.getNumber("EQUATORIAL_EOD_COORD")
        while not (telescope_radec):
            time.sleep(0.5)
            telescope_radec = device_telescope.getNumber("EQUATORIAL_EOD_COORD")
        telescope_radec[0].value = vega["ra"]
        telescope_radec[1].value = vega["dec"]
        self.indiclient.sendNewNumber(telescope_radec)
        # and wait for the scope has finished moving
        # while telescope_radec.s == PyIndi.IPS_BUSY:
        #     print("Scope Moving ", telescope_radec[0].value, telescope_radec[1].value)
        #     time.sleep(2)
        # -----
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

    def get_status_and_broadcast(self):
        c_status = {
            "message_id": uuid.uuid4(),
            "timestamput": datetime.now(timezone.utc),
            # "camera": self.device_status,
        }
        for key in self.device_status.keys():
            c_status[key] = self.device_status[key]

        status = {"camera": c_status}
        xml_format = xmltodict.unparse(status, pretty=True)

        print("/topic/" + self.config["outgoing_topic"])

        self.conn.send(
            body=xml_format,
            destination="/topic/" + self.config["outgoing_topic"],
        )

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
            # while not (self.indiclient.blobEvent.set):
            #     self.indiclient.blobEvent.wait(timeout=0.5)
            #     self.get_status_and_broadcast()

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
