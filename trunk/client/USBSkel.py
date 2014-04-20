import os

from USB import *
from USBDevice import *
from USBConfiguration import *
from USBInterface import *
from USBEndpoint import *
from USBClass import *

from util import *

class USBSkelClass(USBClass):
    name = "USB skel storage class"

class USBSkellInterface(USBInterface):
    name = "USB skel interface"

    def __init__(self, verbose=0):
        descriptors = { }

        self.ep_from_host = USBEndpoint(
                1,          # endpoint number
                USBEndpoint.direction_out,
                USBEndpoint.transfer_type_bulk,
                USBEndpoint.sync_type_none,
                USBEndpoint.usage_type_data,
                16384,      # max packet size
                0,          # polling interval, see USB 2.0 spec Table 9-13
                self.handle_data_available    # handler function
        )
        self.ep_to_host = USBEndpoint(
                3,          # endpoint number
                USBEndpoint.direction_in,
                USBEndpoint.transfer_type_bulk,
                USBEndpoint.sync_type_none,
                USBEndpoint.usage_type_data,
                16384,      # max packet size
                0,          # polling interval, see USB 2.0 spec Table 9-13
                None        # handler function
        )
        USBInterface.__init__(
                self,
                0,          # interface number
                0,          # alternate setting
                1337,       # interface class: ???
                0,          # subclass: ???
                0x50,       # protocol: bulk-only (BBB) transport
                0,          # string index
                verbose,
                [ self.ep_from_host, self.ep_to_host ],
                descriptors
        )
        self.device_class = USBSkelClass()
        self.device_class.set_interface(self)
        
    def handle_data_available(self, data):
        print(self.name, "handling", len(data), "bytes of data")

class USBSkelDevice(USBDevice):
    name = "USB skel device"
    def __init__(self, maxusb_app, verbose=0):
    
        interface = USBSkelInterface(verbose=verbose)

        config = USBConfiguration(
                1,                                          # index
                "skel desc",                                # string desc
                [ interface ]                               # interfaces
        )

        USBDevice.__init__(
                self,
                maxusb_app,
                0,                      # device class
                0,                      # device subclass
                0,                      # protocol release number
                64,                     # max packet size for endpoint 0
                0xfff0,                 # vendor id: skel
                0xfff0,                 # product id: skel
                0x0003,                 # device revision
                "hacker",               # manufacturer string
                "facedancer",           # product string
                "1337",                 # serial number string
                [ config ],
                verbose=verbose
        )

    def disconnect(self):
        USBDevice.disconnect(self)

