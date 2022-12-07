"""
Created on Feb 7, 2022

@author: dlytle
"""

from pwi4_client import PWI4
import psutil
import subprocess
import time
import os


class PlanewaveMountTalk(object):
    """
    Communications with PlaneWave Mount.
    """

    def __init__(self, parent, host, port):
        self.parent = parent
        self.mount_status = ""

        # Check to see if PWI4 is running, if not, start it.
        if self.checkIfProcessRunning("run-pwi4"):
            print("PWI4 already running.")
            # Connect to PWI4.
            self.pwi4 = PWI4(host=host, port=port)
        else:
            print("PWI4 not running, starting...")
            # Set the display to a "virtual" display so X will work
            # without screen.
            os.environ["DISPLAY"] = ":6.1"
            # Call the routine that will start PWI4 as a seperate process.
            subprocess.Popen("./run-pwi4", cwd="/home/lorax/PWI4/pwi-4.0.11beta10")
            # Sleep 10 seconds to let PWI4 start up.
            time.sleep(10)
            # Connect to PWI4.
            self.pwi4 = PWI4(host=host, port=port)
        self.parent.mount_status = self.pwi4.status()
        print("PlaneWaveMountTalk: finished initialization")

    def checkIfProcessRunning(self, processName):

        # Iterate over the all the running process
        for proc in psutil.process_iter():
            try:
                # Check if process name contains the given name string.
                if processName in proc.name():
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        return False

    def send_command_to_mount(self, mount_command):
        # s = self.pwi4.status()
        # s = self.pwi4.mount_connect()
        # Strip off everything up to the first parenthesis
        if "(" in mount_command:
            mcom = mount_command[0 : mount_command.find("(")]
        else:
            mcom = mount_command
        # print(mcom)

        if mcom == "enableMount":
            print("Enable the Mount")
            self.parent.mount_status = self.pwi4.mount_enable(0)
            self.parent.mount_status = self.pwi4.mount_enable(1)

        elif mcom == "disableMount":
            print("Disable the Mount")

        elif mcom == "connectMount":
            print("Connect the Mount")
            self.mount_status = self.pwi4.status()
            if not self.mount_status.mount.is_connected:
                print("Connecting to mount...")
                self.mount_status = self.pwi4.mount_connect()
                print("Mount connected:", self.mount_status.mount.is_connected)
            print(
                "  RA/Dec: %.4f, %.4f"
                % (
                    self.mount_status.mount.ra_j2000_hours,
                    self.mount_status.mount.dec_j2000_degs,
                )
            )
            self.parent.mount_status = self.mount_status

        elif mcom == "disconnectMount":
            print("Disconnecting from mount...")
            self.parent.mount_status = self.pwi4.mount_disconnect()

        elif mcom == "homeMount":
            print("Home the Mount")
            self.parent.mount_status = self.pwi4.mount_find_home()

        elif mcom == "parkMount":
            print("Park the Mount")
            self.parent.mount_status = self.pwi4.mount_park()

        elif mcom == "status":
            # print("doing status")
            self.parent.mount_status = self.pwi4.status()
            # print(self.parent.mount_status.mount.is_slewing)

        elif mcom == "gotoAltAz":
            # Get the arguments.
            # gotoAltAz(45.0, 200.0)
            alt = float(
                mount_command[mount_command.find("(") + 1 : mount_command.find(",")]
            )
            az = float(
                mount_command[mount_command.find(",") + 2 : mount_command.find(")")]
            )
            print(mount_command)
            print("Slewing...")
            self.parent.mount_status = self.pwi4.mount_goto_alt_az(alt, az)

        else:
            print("Unknown command")

        return ()
