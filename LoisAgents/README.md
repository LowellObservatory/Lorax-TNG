-----
This directory will contain LOIS hardware-specific Agents and message 
translation clients.

LORAX should be able to communicate with LOIS cameras in the same way that the
LOUIs communicate -- over the broker.  The modules herein translate the LORAX
command set into the LOUI/LOIS command set, making LOIS cameras look like any
other camera in LORAX, and make LORAX look like the LOUIs to the LOIS
processes.

The user interface to LORAX developed for classical observing will therefore be
a drop-in replacement for the LOUIs!

TPEB, 11/4/22
