# USBDevice.py
#
# Contains class definitions for USBDevice and USBDeviceRequest.

from USB import *

class USBDevice:
    name = "generic device"

    def __init__(self, maxusb_app, device_class, device_subclass,
            protocol_rel_num, max_packet_size_ep0, vendor_id, product_id,
            device_rev, manufacturer_string, product_string,
            serial_number_string, configurations=[], descriptors={},
            verbose=0):
        self.maxusb_app = maxusb_app
        self.verbose = verbose

        self.strings = [ ]

        self.usb_spec_version           = 0x0001
        self.device_class               = device_class
        self.device_subclass            = device_subclass
        self.protocol_rel_num           = protocol_rel_num
        self.max_packet_size_ep0        = max_packet_size_ep0
        self.vendor_id                  = vendor_id
        self.product_id                 = product_id
        self.device_rev                 = device_rev
        self.manufacturer_string_id     = self.get_string_id(manufacturer_string)
        self.product_string_id          = self.get_string_id(product_string)
        self.serial_number_string_id    = self.get_string_id(serial_number_string)

        # maps from USB.desc_type_* to bytearray OR callable
        self.descriptors = descriptors
        self.descriptors[USB.desc_type_device] = self.get_descriptor
        self.descriptors[USB.desc_type_configuration] = self.handle_get_configuration_descriptor_request
        self.descriptors[USB.desc_type_string] = self.handle_get_string_descriptor_request

        self.config_num = -1
        self.configuration = None
        self.configurations = configurations

        for c in self.configurations:
            csi = self.get_string_id(c.configuration_string)
            c.set_configuration_string_index(csi)

            for i in c.interfaces:
                i.device = self

        self.state = USB.state_detached
        self.ready = False

        self.address = 0

        self.setup_request_handlers()

    def get_string_id(self, s):
        try:
            i = self.strings.index(s)
        except ValueError:
            # string descriptors start at index 1
            self.strings.append(s)
            i = len(self.strings)

        return i

    def setup_request_handlers(self):
        # see table 9-4 of USB 2.0 spec, page 279
        self.request_handlers = {
             0 : self.handle_get_status_request,
             1 : self.handle_clear_feature_request,
             3 : self.handle_set_feature_request,
             5 : self.handle_set_address_request,
             6 : self.handle_get_descriptor_request,
             7 : self.handle_set_descriptor_request,
             8 : self.handle_get_configuration_request,
             9 : self.handle_set_configuration_request,
            10 : self.handle_get_interface_request,
            11 : self.handle_set_interface_request,
            12 : self.handle_synch_frame_request
        }

    def connect(self):
        self.maxusb_app.connect(self)

        # skipping USB.state_attached may not be strictly correct (9.1.1.{1,2})
        self.state = USB.state_powered

    def disconnect(self):
        self.maxusb_app.disconnect()

        self.state = USB.state_detached

    def run(self):
        self.maxusb_app.service_irqs()

    def ack_status_stage(self):
        self.maxusb_app.ack_status_stage()

    def get_descriptor(self, n):
        d = bytearray([
            18,         # length of descriptor in bytes
            1,          # descriptor type 1 == device
            (self.usb_spec_version >> 8) & 0xff,
            self.usb_spec_version & 0xff,
            self.device_class,
            self.device_subclass,
            self.protocol_rel_num,
            self.max_packet_size_ep0,
            (self.vendor_id >> 8) & 0xff,
            self.vendor_id & 0xff,
            (self.product_id >> 8) & 0xff,
            self.product_id & 0xff,
            (self.device_rev >> 8) & 0xff,
            self.device_rev & 0xff,
            self.manufacturer_string_id,
            self.product_string_id,
            self.serial_number_string_id,
            len(self.configurations)
        ])

        return d

    # IRQ handlers
    #####################################################

    def handle_request(self, req):
        if self.verbose > 3:
            print(self.name, "received request", req)

        # figure out the intended recipient
        if req.get_recipient() == USB.request_recipient_device:
            recipient = self
        elif req.get_recipient() == USB.request_recipient_interface:
            recipient = self.configuration.interfaces[req.index]
        elif req.get_recipient() == USB.request_recipient_endpoint:
            try:
                recipient = self.endpoints[req.index]
            except KeyError:
                self.maxusb_app.stall_ep0()
                return

        # and then the type
        if req.get_type() == USB.request_type_standard:
            handler = recipient.request_handlers[req.request]
            handler(req)
        elif req.get_type() == USB.request_type_class:
            # HACK: evidently, FreeBSD doesn't pay attention to the device
            # until it sends a GET_STATUS(class) message
            self.ready = True
            self.maxusb_app.stall_ep0()
        elif req.get_type() == USB.request_type_vendor:
            self.maxusb_app.stall_ep0()

    def handle_data_available(self, ep_num, data):
        if self.state == USB.state_configured and ep_num in self.endpoints:
            endpoint = self.endpoints[ep_num]
            endpoint.handler(data)

    def handle_buffer_available(self, ep_num):
        if self.state == USB.state_configured and ep_num in self.endpoints:
            endpoint = self.endpoints[ep_num]
            endpoint.handler()
    
    # standard request handlers
    #####################################################

    # USB 2.0 specification, section 9.4.5 (p 282 of pdf)
    def handle_get_status_request(self, req):
        print(self.name, "received GET_STATUS request")

        # self-powered and remote-wakeup (USB 2.0 Spec section 9.4.5)
        response = b'\x03\x00'
        self.maxusb_app.send_on_endpoint(0, response)

    # USB 2.0 specification, section 9.4.1 (p 280 of pdf)
    def handle_clear_feature_request(self, req):
        print(self.name, "received CLEAR_FEATURE request with type 0x%02x and value 0x%02x" \
                % (req.request_type, req.value))

    # USB 2.0 specification, section 9.4.9 (p 286 of pdf)
    def handle_set_feature_request(self, req):
        print(self.name, "received SET_FEATURE request")

    # USB 2.0 specification, section 9.4.6 (p 284 of pdf)
    def handle_set_address_request(self, req):
        self.address = req.value
        self.state = USB.state_address
        self.ack_status_stage()

        if self.verbose > 2:
            print(self.name, "received SET_ADDRESS request for address",
                    self.address)

    # USB 2.0 specification, section 9.4.3 (p 281 of pdf)
    def handle_get_descriptor_request(self, req):
        dtype  = (req.value >> 8) & 0xff
        dindex = req.value & 0xff
        lang   = req.index
        n      = req.length

        response = None

        if self.verbose > 2:
            print(self.name, ("received GET_DESCRIPTOR req %d, index %d, " \
                    + "language 0x%04x, length %d") \
                    % (dtype, dindex, lang, n))

        # TODO: handle KeyError
        response = self.descriptors[dtype]
        if callable(response):
            response = response(dindex)

        if response:
            n = min(n, len(response))
            self.maxusb_app.verbose += 1
            self.maxusb_app.send_on_endpoint(0, response[:n])
            self.maxusb_app.verbose -= 1

            if self.verbose > 5:
                print(self.name, "sent", n, "bytes in response")

    def handle_get_configuration_descriptor_request(self, num):
        return self.configurations[num].get_descriptor()

    def handle_get_string_descriptor_request(self, num):
        if num == 0:
            # HACK: hard-coding baaaaad
            d = bytes([
                    4,      # length of descriptor in bytes
                    3,      # descriptor type 3 == string
                    9,      # language code 0, byte 0
                    4       # language code 0, byte 1
            ])
        else:
            # string descriptors start at 1
            s = self.strings[num-1].encode('utf-16')

            # Linux doesn't like the leading 2-byte Byte Order Mark (BOM);
            # FreeBSD is okay without it
            s = s[2:]

            d = bytearray([
                    len(s) + 2,     # length of descriptor in bytes
                    3               # descriptor type 3 == string
            ])
            d += s

        return d

    # USB 2.0 specification, section 9.4.8 (p 285 of pdf)
    def handle_set_descriptor_request(self, req):
        print(self.name, "received SET_DESCRIPTOR request")

    # USB 2.0 specification, section 9.4.2 (p 281 of pdf)
    def handle_get_configuration_request(self, req):
        print(self.name, "received GET_CONFIGURATION request with data 0x%02x" \
                % req.data)

    # USB 2.0 specification, section 9.4.7 (p 285 of pdf)
    def handle_set_configuration_request(self, req):
        print(self.name, "received SET_CONFIGURATION request")

        # configs are one-based
        self.config_num = req.value - 1
        self.configuration = self.configurations[self.config_num]
        self.state = USB.state_configured

        # collate endpoint numbers
        self.endpoints = { }
        for i in self.configuration.interfaces:
            for e in i.endpoints:
                self.endpoints[e.number] = e

        # HACK: blindly acknowledge request
        self.ack_status_stage()

    # USB 2.0 specification, section 9.4.4 (p 282 of pdf)
    def handle_get_interface_request(self, req):
        print(self.name, "received GET_INTERFACE request")

        if req.index == 0:
            # HACK: currently only support one interface
            self.maxusb_app.send_on_endpoint(0, b'\x00')
        else:
            self.maxusb_app.stall_ep0()

    # USB 2.0 specification, section 9.4.10 (p 288 of pdf)
    def handle_set_interface_request(self, req):
        print(self.name, "received SET_INTERFACE request")

    # USB 2.0 specification, section 9.4.11 (p 288 of pdf)
    def handle_synch_frame_request(self, req):
        print(self.name, "received SYNCH_FRAME request")


class USBDeviceRequest:
    def __init__(self, raw_bytes):
        """Expects raw 8-byte setup data request packet"""

        self.request_type   = raw_bytes[0]
        self.request        = raw_bytes[1]
        self.value          = (raw_bytes[3] << 8) | raw_bytes[2]
        self.index          = (raw_bytes[5] << 8) | raw_bytes[4]
        self.length         = (raw_bytes[7] << 8) | raw_bytes[6]

    def __str__(self):
        s = "dir=%d, type=%d, rec=%d, r=%d, v=%d, i=%d, l=%d" \
                % (self.get_direction(), self.get_type(), self.get_recipient(),
                   self.request, self.value, self.index, self.length)
        return s

    def raw(self):
        """returns request as bytes"""
        b = bytes([ self.request_type, self.request,
                    (self.value  >> 8) & 0xff, self.value  & 0xff,
                    (self.index  >> 8) & 0xff, self.index  & 0xff,
                    (self.length >> 8) & 0xff, self.length & 0xff
                  ])
        return b

    def get_direction(self):
        return (self.request_type >> 7) & 0x01

    def get_type(self):
        return (self.request_type >> 5) & 0x03

    def get_recipient(self):
        return self.request_type & 0x1f

