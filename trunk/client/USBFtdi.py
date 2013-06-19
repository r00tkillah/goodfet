# USBFtdi.py
#
# Contains class definitions to implement a USB FTDI chip.

from USB import *
from USBDevice import *
from USBConfiguration import *
from USBInterface import *
from USBEndpoint import *
from USBVendor import *

from util import *

class USBFtdiVendor(USBVendor):
    name = "USB FTDI vendor"

    def setup_request_handlers(self):
        self.request_handlers = {
             0 : self.handle_reset_request,
             1 : self.handle_modem_ctrl_request,
             2 : self.handle_set_flow_ctrl_request,
             3 : self.handle_set_baud_rate_request,
             4 : self.handle_set_data_request,
             5 : self.handle_get_status_request,
             6 : self.handle_set_event_char_request,
             7 : self.handle_set_error_char_request,
             9 : self.handle_set_latency_timer_request,
            10 : self.handle_get_latency_timer_request
        }

    def handle_reset_request(self, req):
        if self.verbose > 0:
            print(self.name, "received reset request")

        self.interface.configuration.device.maxusb_app.send_on_endpoint(0, b'')

    def handle_modem_ctrl_request(self, req):
        if self.verbose > 0:
            print(self.name, "received modem_ctrl request")

        dtr = req.value[1] & 0x01
        rts = (req.value[1] & 0x02) >> 1
        dtren = req.value[0] & 0x01
        rtsen = (req.value[0] & 0x02) >> 1

        if dtren:
            print("DTR is enabled, value", dtr)
        if rtsen:
            print("RTS is enabled, value", rts)

        self.interface.configuration.device.maxusb_app.send_on_endpoint(0, b'')

    def handle_set_flow_ctrl_request(self, req):
        if self.verbose > 0:
            print(self.name, "received set_flow_ctrl request")

        dtr = req.value[1] & 0x01
        if req.value[1] == 0:
            print("SET_FLOW_CTRL to no handshaking")
        if req.value[1] & 0x01:
            print("SET_FLOW_CTRL for RTS/CTS handshaking")
        if req.value[1] & 0x02:
            print("SET_FLOW_CTRL for DTR/DSR handshaking")
        if req.value[1] & 0x04:
            print("SET_FLOW_CTRL for XON/XOFF handshaking")

        self.interface.configuration.device.maxusb_app.send_on_endpoint(0, b'')

    def handle_set_baud_rate_request(self, req):
        if self.verbose > 0:
            print(self.name, "received set_baud_rate request")

        dtr = req.value[1] & 0x01
        print("baud rate set to", req.value[1])

        self.interface.configuration.device.maxusb_app.send_on_endpoint(0, b'')

    def handle_set_data_request(self, req):
        if self.verbose > 0:
            print(self.name, "received set_data request")

        self.interface.configuration.device.maxusb_app.send_on_endpoint(0, b'')

    def handle_get_status_request(self, req):
        if self.verbose > 0:
            print(self.name, "received get_status request")

        self.interface.configuration.device.maxusb_app.send_on_endpoint(0, b'')

    def handle_set_event_char_request(self, req):
        if self.verbose > 0:
            print(self.name, "received set_event_char request")

        self.interface.configuration.device.maxusb_app.send_on_endpoint(0, b'')

    def handle_set_error_char_request(self, req):
        if self.verbose > 0:
            print(self.name, "received set_error_char request")

        self.interface.configuration.device.maxusb_app.send_on_endpoint(0, b'')

    def handle_set_latency_timer_request(self, req):
        if self.verbose > 0:
            print(self.name, "received set_latency_timer request")

        self.interface.configuration.device.maxusb_app.send_on_endpoint(0, b'')

    def handle_get_latency_timer_request(self, req):
        if self.verbose > 0:
            print(self.name, "received get_latency_timer request")

        # bullshit value
        self.interface.configuration.device.maxusb_app.send_on_endpoint(0, b'\x01')


class USBFtdiInterface(USBInterface):
    name = "USB FTDI interface"

    def __init__(self, verbose=0):
        descriptors = { }

        endpoints = [
            USBEndpoint(
                1,          # endpoint number
                USBEndpoint.direction_out,
                USBEndpoint.transfer_type_bulk,
                USBEndpoint.sync_type_none,
                USBEndpoint.usage_type_data,
                16384,      # max packet size
                0,          # polling interval, see USB 2.0 spec Table 9-13
                self.handle_data_available      # handler function
            ),
            USBEndpoint(
                3,          # endpoint number
                USBEndpoint.direction_in,
                USBEndpoint.transfer_type_bulk,
                USBEndpoint.sync_type_none,
                USBEndpoint.usage_type_data,
                16384,      # max packet size
                0,          # polling interval, see USB 2.0 spec Table 9-13
                self.handle_buffer_available    # handler function
            )
        ]

        # TODO: un-hardcode string index (last arg before "verbose")
        USBInterface.__init__(
                self,
                0,          # interface number
                0,          # alternate setting
                0xff,       # interface class: vendor-specific
                0xff,       # subclass: vendor-specific
                0xff,       # protocol: vendor-specific
                0,          # string index
                verbose,
                endpoints,
                descriptors
        )

        self.device_vendor = USBFtdiVendor()
        self.device_vendor.set_interface(self)

    def handle_buffer_available(self):
        pass

    def handle_data_available(self, data):
        pass


class USBFtdiDevice(USBDevice):
    name = "USB FTDI device"

    def __init__(self, maxusb_app, verbose=0):
        interface = USBFtdiInterface(verbose=verbose)

        config = USBConfiguration(
                1,                                          # index
                "FTDI config",                              # string desc
                [ interface ]                               # interfaces
        )

        USBDevice.__init__(
                self,
                maxusb_app,
                0,                      # device class
                0,                      # device subclass
                0,                      # protocol release number
                64,                     # max packet size for endpoint 0
                0x0403,                 # vendor id: FTDI
                0x8372,                 # product id: FT232 USB-Serial (UART) IC
                0x0001,                 # device revision
                "GoodFET",              # manufacturer string
                "FTDI Emulator",        # product string
                "S/N3420E",             # serial number string
                [ config ],
                verbose=verbose
        )

