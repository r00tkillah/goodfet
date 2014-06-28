# USBLogitechDj.py
#
# Contains class definitions to implement a Logitech Dj

from USB import *
from USBDevice import *
from USBConfiguration import *
from USBInterface import *
from USBEndpoint import *


# I don't really know why we need these, but we sort of do
class USBLogiInterface1(USBInterface):
    name = "logitech interface"
    hid_descriptor = b'\x09\x21\x11\x01\x00\x01\x22\x3B\x00'
    report_descriptor = b'\x05\x01\x09\x06\xA1\x01\x05\x07\x19\xE0\x29\xE7\x15\x00\x25\x01\x75\x01\x95\x08\x81\x02\x95\x01\x75\x08\x81\x01\x19\x00\x29\x65\x15\x00\x25\x65\x75\x08\x95\x01\x81\x00\xC0'

    def __init__(self, verbose=0):
        descriptors = {
            USB.desc_type_hid    : self.hid_descriptor,
            USB.desc_type_report : self.report_descriptor
            }
        self.endpoint = USBEndpoint(
                3,          # endpoint number
                USBEndpoint.direction_in,
                USBEndpoint.transfer_type_interrupt,
                USBEndpoint.sync_type_none,
                USBEndpoint.usage_type_data,
                8,      # max packet size
                8,         # polling interval, see USB 2.0 spec Table 9-13
                self.handle_buffer_available
        )
        
        USBInterface.__init__(
                self,
                0,          # interface number
                0,          # alternate setting
                3,          # interface class
                1,          # subclass
                1,          # protocol
                0,          # string index
                verbose,
                [ self.endpoint ],
                descriptors
        )

    def handle_buffer_available(self):
        print("handling buffer in interface1\n")

class USBLogiInterface2(USBInterface):
    name = "logitech interface"
    hid_descriptor = b'\x09\x21\x11\x01\x00\x01\x22\x3B\x00'
    report_descriptor = b'\x05\x01\x09\x06\xA1\x01\x05\x07\x19\xE0\x29\xE7\x15\x00\x25\x01\x75\x01\x95\x08\x81\x02\x95\x01\x75\x08\x81\x01\x19\x00\x29\x65\x15\x00\x25\x65\x75\x08\x95\x01\x81\x00\xC0'

    def __init__(self, verbose=0):
        descriptors = {
            USB.desc_type_hid    : self.hid_descriptor,
            USB.desc_type_report : self.report_descriptor
            }
        self.endpoint = USBEndpoint(
                3,          # endpoint number
                USBEndpoint.direction_in,
                USBEndpoint.transfer_type_interrupt,
                USBEndpoint.sync_type_none,
                USBEndpoint.usage_type_data,
                8,      # max packet size
                8,         # polling interval, see USB 2.0 spec Table 9-13
                self.handle_buffer_available
        )
        
        USBInterface.__init__(
                self,
                1,          # interface number
                0,          # alternate setting
                3,          # interface class
                1,          # subclass
                2,          # protocol
                0,          # string index
                verbose,
                [ self.endpoint ],
                descriptors
        )

    def handle_buffer_available(self):
        print("handling buffer in interface1\n")

#this is the interface we care about
class USBKeyboardInterface(USBInterface):
    name = "DJ Interface"

    # this one was lifted from USB keyboard
    hid_descriptor =       b'\x09\x21\x10\x01\x00\x01\x22\x2b\x00'

    # this was lifted from rela hardware
    filched_hid_descriptor=b'\x09\x21\x11\x01\x00\x01\x22\x62\x00'

    # unsure where this one came from
    descriptor_7 = b'\x05\x01\x09\x02\xa1\x01\x85\x02\x09\x01\xa1\x00\x05\x09\x19\x01\x29\x10\x15\x00\x25\x01\x95\x10\x75\x01\x81\x02\x05\x01\x16\x01\xf8\x26\xff\x07\x75\x0c\x95\x02\x09\x30\x09\x31\x81\x06\x15\x81\x25\x7f\x75\x08\x95\x01\x09\x38\x81\x06\x05\x0c\x0a\x38\x02\x95\x01\x81\x06\xc0\xc0'

    # descriptor_6 is 98 bytes (0x62)
    # this was actually seen and is referneced in some dj RE docs
    descriptor_6 = b'\x06\x00\xff\x09\x01\xa1\x01\x85\x10\x75\x08\x95\x06\x15\x00\x26\xff\x00\x09\x01\x81\x00\x09\x01\x91\x00\xc0\x06\x00\xff\x09\x02\xa1\x01\x85\x11\x75\x08\x95\x13\x15\x00\x26\xff\x00\x09\x02\x81\x00\x09\x02\x91\x00\xc0\x06\x00\xff\x09\x04\xa1\x01\x85\x20\x75\x08\x95\x0e\x15\x00\x26\xff\x00\x09\x41\x81\x00\x09\x41\x91\x00\x85\x21\x95\x1f\x15\x00\x26\xff\x00\x09\x42\x81\x00\x09\x42\x91\x00\xc0'

    # using this one causes it to fail in switch_to_dj_mode
    # this one was filched from USBKeyboard
    descriptor_kb = b'\x05\x01\x09\x06\xA1\x01\x05\x07\x19\xE0\x29\xE7\x15\x00\x25\x01\x75\x01\x95\x08\x81\x02\x95\x01\x75\x08\x81\x01\x19\x00\x29\x65\x15\x00\x25\x65\x75\x08\x95\x01\x81\x00\xC0'

    def __init__(self, verbose=0):
        descriptors = { 
                USB.desc_type_hid    : self.filched_hid_descriptor,
                USB.desc_type_report : self.descriptor_6,
        }

        self.endpoint = USBEndpoint(
                3,          # endpoint number
                USBEndpoint.direction_in,
                USBEndpoint.transfer_type_interrupt,
                USBEndpoint.sync_type_none,
                USBEndpoint.usage_type_data,
                16384,      # max packet size
                10,         # polling interval, see USB 2.0 spec Table 9-13
                self.handle_buffer_available    # handler function
        )

        # TODO: un-hardcode string index (last arg before "verbose")
        USBInterface.__init__(
                self,
                2,          # interface number
                0,          # alternate setting
                3,          # interface class
                0,          # subclass
                0,          # protocol
                0,          # string index
                verbose,
                [ self.endpoint ],
                descriptors
        )

        # "l<KEY UP>s<KEY UP><ENTER><KEY UP>"
        empty_preamble = [ 0x00 ] * 10
        text = [ 0x0f, 0x00, 0x16, 0x00, 0x28, 0x00 ]

        self.keys = [ chr(x) for x in empty_preamble + text ]

    def handle_buffer_available(self):
        return
        print("handle_buffer_availble!")
        self.endpoint.send(data)


class USBKeyboardDevice(USBDevice):
    name = "USB keyboard device"

    def __init__(self, maxusb_app, verbose=0):
        config = USBConfiguration(
                1,                                          # index
                "Emulated Keyboard",    # string desc
                [ USBLogiInterface1(), USBLogiInterface2(), USBKeyboardInterface() ]                  # interfaces
        )

        USBDevice.__init__(
                self,
                maxusb_app,
                0,                      # device class
                0,                      # device subclass
                0,                      # protocol release number
                64,                     # max packet size for endpoint 0
                0x046d,                 # vendor id
                0xc52b,                 # product id
                0x3412,                 # device revision
                "Logitech",             # manufacturer string
                "Unifying Receiver",         # product string
                "0",                    # serial number string
                [ config ],
                verbose=verbose
        )

