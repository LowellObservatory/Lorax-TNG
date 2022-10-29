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
from IndiClient import IndiClient


class SBIGCamera(SubAgent):
    def __init__(self, logger, conn, config):
        print("in SBIGCamera.init")
        SubAgent.__init__(self, logger, conn, config)

        # Get the host and port for the connection to camera.
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

        # This is a special property of the CCD_Simulator.
        # the CCD_Simulator requires an RA and DEC before it
        # will take an image.  One way to do this is load
        # the telescope simulator and connect to it.
        # The other way is to set this property in the
        # CCD simulator.  We do that here.
        eqpe = device_ccd.getNumber("EQUATORIAL_PE")
        while not eqpe:
            print("  Waiting for EQ_PE...")
            time.sleep(0.5)
            eqpe = device_ccd.getNumber("EQUATORIAL_PE")

        eqpe[0].value = 0.0
        eqpe[1].value = 0.0
        self.indiclient.sendNewNumber(eqpe)

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

            # Check the required exposure properties
            if not self.exptime:
                print("WARNING: Must specify exposure time before exposing!")
                return
            if not self.exptype:
                print("WARNING: Must specify exposure type before exposing!")
                return

            # Say what we're going to do
            print(f"Exposing {self.exptype} frame for {self.exptime:.2f}s...")

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
