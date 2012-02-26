#!/usr/bin/env python
# GoodFET Client Library for Maxim USB Chips.
# 
# (C) 2012 Travis Goodspeed <travis at radiantmachines.com>
#
# This code is being rewritten and refactored.  You've been warned!

import sys, time, string, cStringIO, struct, glob, os;

from GoodFET import GoodFET;

#Handy registers.
rEP0FIFO=0
rEP1OUTFIFO=1
rEP2INFIFO=2
rEP3INFIFO=3
rSUDFIFO=4
rEP0BC=5
rEP1OUTBC=6
rEP2INBC=7
rEP3INBC=8
rEPSTALLS=9
rCLRTOGS=10
rEPIRQ=11
rEPIEN=12
rUSBIRQ=13
rUSBIEN=14
rUSBCTL=15
rCPUCTL=16
rPINCTL=17
rREVISION=18
rFNADDR=19
rIOPINS=20

# R11 EPIRQ register bits
bmSUDAVIRQ =0x20
bmIN3BAVIRQ =0x10
bmIN2BAVIRQ =0x08
bmOUT1DAVIRQ= 0x04
bmOUT0DAVIRQ= 0x02
bmIN0BAVIRQ =0x01

# R12 EPIEN register bits
bmSUDAVIE   =0x20
bmIN3BAVIE  =0x10
bmIN2BAVIE  =0x08
bmOUT1DAVIE =0x04
bmOUT0DAVIE =0x02
bmIN0BAVIE  =0x01


# ************************
# Standard USB Requests
SR_GET_STATUS		=0x00	# Get Status
SR_CLEAR_FEATURE	=0x01	# Clear Feature
SR_RESERVED		=0x02	# Reserved
SR_SET_FEATURE		=0x03	# Set Feature
SR_SET_ADDRESS		=0x05	# Set Address
SR_GET_DESCRIPTOR	=0x06	# Get Descriptor
SR_SET_DESCRIPTOR	=0x07	# Set Descriptor
SR_GET_CONFIGURATION	=0x08	# Get Configuration
SR_SET_CONFIGURATION	=0x09	# Set Configuration
SR_GET_INTERFACE	=0x0a	# Get Interface
SR_SET_INTERFACE	=0x0b	# Set Interface

# Get Descriptor codes	
GD_DEVICE		=0x01	# Get device descriptor: Device
GD_CONFIGURATION	=0x02	# Get device descriptor: Configuration
GD_STRING		=0x03	# Get device descriptor: String
GD_HID	            	=0x21	# Get descriptor: HID
GD_REPORT	        =0x22	# Get descriptor: Report

# SETUP packet offsets
bmRequestType           =0
bRequest       	        =1
wValueL			=2
wValueH			=3
wIndexL			=4
wIndexH			=5
wLengthL		=6
wLengthH		=7

# HID bRequest values
GET_REPORT		=1
GET_IDLE		=2
GET_PROTOCOL            =3
SET_REPORT		=9
SET_IDLE		=0x0A
SET_PROTOCOL            =0x0B
INPUT_REPORT            =1




class GoodFETMAXUSB(GoodFET):
    MAXUSBAPP=0x40;
    def MAXUSBsetup(self):
        """Move the FET into the MAXUSB application."""
        self.writecmd(self.MAXUSBAPP,0x10,0,self.data); #MAXUSB/SETUP
        print "Connected to MAX342x Rev. %x" % (self.rreg(rREVISION));
        self.wreg(rPINCTL,0x18); #Set duplex and negative INT level.
        
    def MAXUSBtrans8(self,byte):
        """Read and write 8 bits by MAXUSB."""
        data=self.MAXUSBtrans([byte]);
        return ord(data[0]);
    
    def MAXUSBtrans(self,data):
        """Exchange data by MAXUSB."""
        self.data=data;
        self.writecmd(self.MAXUSBAPP,0x00,len(data),data);
        return self.data;

    def rreg(self,reg):
        """Peek 8 bits from a register."""
        data=[reg<<3,0];
        self.writecmd(self.MAXUSBAPP,0x00,len(data),data);
        return ord(self.data[1]);
    def rregAS(self,reg):
        """Peek 8 bits from a register, setting AS."""
        data=[(reg<<3)|1,0];
        self.writecmd(self.MAXUSBAPP,0x00,len(data),data);
        return ord(self.data[1]);
    def wreg(self,reg,value):
        """Poke 8 bits into a register."""
        data=[(reg<<3)|2,value];
        self.writecmd(self.MAXUSBAPP,0x00,len(data),data);        
        return value;
    def wregAS(self,reg,value):
        """Poke 8 bits into a register, setting AS."""
        data=[(reg<<3)|3,value];
        self.writecmd(self.MAXUSBAPP,0x00,len(data),data);        
        return value;
    def readbytes(self,reg,length):
        """Peek some bytes from a register."""
        data=[(reg<<3)]+range(0,length);
        self.writecmd(self.MAXUSBAPP,0x00,len(data),data);
        toret=self.data[1:len(self.data)];
        ashex="";
        for foo in toret:
            ashex=ashex+(" %02x"%ord(foo));
        print "GET %02x==%s" % (reg,ashex);
        return toret;
    def writebytes(self,reg,tosend):
        """Poke some bytes into a register."""
        data="";
        if type(tosend)==str:
            data=chr((reg<<3)|2)+tosend;
        else:
            data=[(reg<<3)|2]+tosend;
            ashex="";
            for foo in tosend:
                ashex=ashex+(" %02x"%foo);
            print "PUT %02x:=%s" % (reg,ashex)
        self.writecmd(self.MAXUSBAPP,0x00,len(data),data);
    def usb_connect(self):
        """Connect the USB port."""
        
        #disconnect D+ pullup if host turns off VBUS
        self.wreg(rUSBCTL,0x48);
    def STALL_EP0(self):
        """Stall for an unknown event."""
        print "Stalling.";
        self.wreg(rEPSTALLS,0x23); #All three stall bits.
    def SETBIT(self,reg,val):
        """Set a bit in a register."""
        self.wreg(reg,self.rreg(reg)|val);
class GoodFETMAXUSBHID(GoodFETMAXUSB):
    """This is an example HID keyboard driver, loosely based on the
    MAX3420 examples."""
    def hidinit(self):
        """Initialize a USB HID device."""
        self.usb_connect();
        self.hidrun();
        
    def hidrun(self):
        """Main loop of the USB HID emulator."""
        print "Starting a HID device.  This won't return.";
        while 1:
            self.service_irqs();
    def do_SETUP(self):
        """Handle USB Enumeration"""
        
        #Grab the SETUP packet from the buffer.
        SUD=self.readbytes(rSUDFIFO,8);
        
        #Parse the SETUP packet
        print "Handling a setup packet type 0x%02x" % ord(SUD[bmRequestType]);
        setuptype=(ord(SUD[bmRequestType])&0x60);
        if setuptype==0x00:
            self.std_request(SUD);
        elif setuptype==0x20:
            self.class_request(SUD);
        elif setuptype==0x40:
            self.vendor_request(SUD);
        else:
            print "Unknown request type 0x%02x." % ord(SUD[bmRequestType])
            self.STALL_EP0();
    def class_request(self,SUD):
        """Handle a class request."""
        print "Stalling a class request.";
        self.STALL_EP0();
    def vendor_request(self,SUD):
        print "Stalling a vendor request.";
        self.STALL_EP0();
    def std_request(self,SUD):
        """Handles a standard setup request."""
        setuptype=ord(SUD[bRequest]);
        if setuptype==SR_GET_DESCRIPTOR: self.send_descriptor(SUD);
        elif setuptype==SR_SET_FEATURE: self.feature(1);
        elif setuptype==SR_SET_CONFIGURATION: self.set_configuration(SUD);
        elif setuptype==SR_GET_STATUS: self.get_status(SUD);
        elif setuptype==SR_SET_ADDRESS: self.rregAS(rFNADDR);
        elif setuptype==SR_GET_INTERFACE: self.get_interface(SUD);
        else:
            print "Stalling Unknown standard setup request type %02x" % setuptype;
            
            self.STALL_EP0();
    
    def get_interface(self,SUD):
        """Handles a setup request for SR_GET_INTERFACE."""
        if ord(SUD[wIndexL]==0):
            self.wreg(rEP0FIFO,0);
            self.wregAS(rEP0BC,1);
        else:
            self.STALL_EP0();
    
    #Device Descriptor
    DD=[0x12,	       		# bLength = 18d
        0x01,			# bDescriptorType = Device (1)
        0x00,0x01,		# bcdUSB(L/H) USB spec rev (BCD)
	0x00,0x00,0x00, 	# bDeviceClass, bDeviceSubClass, bDeviceProtocol
	0x40,			# bMaxPacketSize0 EP0 is 64 bytes
	0x6A,0x0B,		# idVendor(L/H)--Maxim is 0B6A
	0x46,0x53,		# idProduct(L/H)--5346
	0x34,0x12,		# bcdDevice--1234
	1,2,3,			# iManufacturer, iProduct, iSerialNumber
	1];
    #Configuration Descriptor
    CD=[0x09,			# bLength
	0x02,			# bDescriptorType = Config
	0x22,0x00,		# wTotalLength(L/H) = 34 bytes
	0x01,			# bNumInterfaces
	0x01,			# bConfigValue
	0x00,			# iConfiguration
	0xE0,			# bmAttributes. b7=1 b6=self-powered b5=RWU supported
	0x01,			# MaxPower is 2 ma
# INTERFACE Descriptor
	0x09,			# length = 9
	0x04,			# type = IF
	0x00,			# IF #0
	0x00,			# bAlternate Setting
	0x01,			# bNum Endpoints
	0x03,			# bInterfaceClass = HID
	0x00,0x00,		# bInterfaceSubClass, bInterfaceProtocol
	0x00,			# iInterface
# HID Descriptor--It's at CD[18]
	0x09,			# bLength
	0x21,			# bDescriptorType = HID
	0x10,0x01,		# bcdHID(L/H) Rev 1.1
	0x00,			# bCountryCode (none)
	0x01,			# bNumDescriptors (one report descriptor)
	0x22,			# bDescriptorType	(report)
	43,0,                   # CD[25]: wDescriptorLength(L/H) (report descriptor size is 43 bytes)
# Endpoint Descriptor
	0x07,			# bLength
	0x05,			# bDescriptorType (Endpoint)
	0x83,			# bEndpointAddress (EP3-IN)		
	0x03,			# bmAttributes	(interrupt)
	64,0,                   # wMaxPacketSize (64)
	10];
    strDesc=[
# STRING descriptor 0--Language string
"\x04\x03\x09\x04",
# [
#         0x04,			# bLength
# 	0x03,			# bDescriptorType = string
# 	0x09,0x04		# wLANGID(L/H) = English-United Sates
# ],
# STRING descriptor 1--Manufacturer ID
"\x0c\x03M\x00a\x00x\x00i\x00m\x00",
# [
#         12,			# bLength
# 	0x03,			# bDescriptorType = string
# 	'M',0,'a',0,'x',0,'i',0,'m',0 # text in Unicode
# ], 
# STRING descriptor 2 - Product ID
"\x18\x03M\x00A\x00X\x003\x004\x002\x000\x00E\x00 \x00E\x00n\x00u\x00m\x00 \x00C\x00o\x00d\x00e\x00",
# [	24,			# bLength
# 	0x03,			# bDescriptorType = string
# 	'M',0,'A',0,'X',0,'3',0,'4',0,'2',0,'0',0,'E',0,' ',0,
#         'E',0,'n',0,'u',0,'m',0,' ',0,'C',0,'o',0,'d',0,'e',0
# ],


# STRING descriptor 3 - Serial Number ID
"\x14\x03S\x00/\x00N\x00 \x003\x004\x002\x000\x00E\x00"
# [       20,			# bLength
# 	0x03,			# bDescriptorType = string
# 	'S',0,				
# 	'/',0,
# 	'N',0,
# 	' ',0,
# 	'3',0,
# 	'4',0,
# 	'2',0,
# 	'0',0,
#         'E',0,
# ]
];
    RepD=[
        0x05,0x01,		# Usage Page (generic desktop)
	0x09,0x06,		# Usage (keyboard)
	0xA1,0x01,		# Collection
	0x05,0x07,		#   Usage Page 7 (keyboard/keypad)
	0x19,0xE0,		#   Usage Minimum = 224
	0x29,0xE7,		#   Usage Maximum = 231
	0x15,0x00,		#   Logical Minimum = 0
	0x25,0x01,		#   Logical Maximum = 1
	0x75,0x01,		#   Report Size = 1
	0x95,0x08,		#   Report Count = 8
	0x81,0x02,		#  Input(Data,Variable,Absolute)
	0x95,0x01,		#   Report Count = 1
	0x75,0x08,		#   Report Size = 8
	0x81,0x01,		#  Input(Constant)
	0x19,0x00,		#   Usage Minimum = 0
	0x29,0x65,		#   Usage Maximum = 101
	0x15,0x00,		#   Logical Minimum = 0,
	0x25,0x65,		#   Logical Maximum = 101
	0x75,0x08,		#   Report Size = 8
	0x95,0x01,		#   Report Count = 1
	0x81,0x00,		#  Input(Data,Variable,Array)
	0xC0]
    def send_descriptor(self,SUD):
        """Send the USB descriptors based upon the setup data."""
        desclen=0;
        reqlen=ord(SUD[wLengthL])+256*ord(SUD[wLengthH]); #16-bit length
        desctype=ord(SUD[wValueH]);
        
        if desctype==GD_DEVICE:
            desclen=self.DD[0];
            ddata=self.DD;
        elif desctype==GD_CONFIGURATION:
            desclen=self.CD[2];
            ddata=self.CD;
        elif desctype==GD_STRING:
            desclen=self.strDesc[ord(SUD[wValueL])][0];
            ddata=self.strDesc[ord(SUD[wValueL])];
        elif desctype==GD_REPORT:
            desclen=self.CD[25];
            ddata=self.RepD;
        
        #TODO Configuration, String, Hid, and Report
        
        if desclen>0:
            sendlen=min(reqlen,desclen);
            self.writebytes(rEP0FIFO,ddata);
            self.wregAS(rEP0BC,sendlen);
        else:
            print "Stalling in send_descriptor() for lack of handler for %02x." % desctype;
            self.STALL_EP0();
    def set_configuration(self,SUD):
        """Set the configuration."""
        bmSUSPIE=0x10;
        configval=ord(SUD[wValueL]);
        if(configval>0):
            self.SETBIT(rUSBIEN,bmSUSPIE);
        self.rregAS(rFNADDR);
    def get_status(self,SUD):
        """Get the USB Setup Status."""
        testbyte=ord(SUD[bmRequestType])
        
        #Toward Device
        if testbyte==0x80:
            self.wreg(rEP0FIFO,0x03); #Enable RWU and self-powered
            self.wreg(rEP0FIFO,0x00); #Second byte is always zero.
            self.wregAS(rEP0BC,2);    #Load byte count, arm transfer, and ack CTL.
        #Toward Interface
        elif testbyte==0x81:
            self.wreg(rEP0FIFO,0x00);
            self.wreg(rEP0FIFO,0x00); #Second byte is always zero.
            self.wregAS(rEP0BC,2);
        #Toward Endpoint
        elif testbyte==0x82:
            if(ord(SUD[wIndexL])==0x83):
                self.wreg(rEP0FIFO,0x01); #Stall EP3
                self.wreg(rEP0FIFO,0x00); #Second byte is always zero.
                self.wregAS(rEP0BC,2);
            else:
                self.STALL_EP0();
        else:
            self.STALL_EP0();
    def service_irqs(self):
        """Handle USB interrupt events."""
        
        epirq=self.rreg(rEPIRQ);
        usbirq=self.rreg(rUSBIRQ);
        
        #Are we being asked for setup data?
        if(epirq&bmSUDAVIRQ): #Setup Data Requested
            self.wreg(rEPIRQ,bmSUDAVIRQ); #Clear the bit
            self.do_SETUP();
        if(epirq&bmIN3BAVIRQ): #EN3-IN packet
            self.do_IN3();
        
    
    typephase=0;
    typestring="                      Python does USB HID!";
    typepos=0;
    
    def asc2hid(self,ascii):
        """Translate ASCII to an USB keycode."""
        a=ascii;
        if a>='a' and a<='z':
            return ord(a)-ord('a')+4;
        elif a>='A' and a<='Z':
            return ord(a)-ord('A')+4;
        elif a==' ':
            return 0x2C; #space
        else:
            return 0; #key-up
    def type_IN3(self):
        """Type next letter in buffer."""
        if self.typepos>=len(self.typestring):
            self.typeletter(0);
        elif self.typephase==0:
            self.typephase=1;
            self.typeletter(0);
        else:
            typephase=0;
            self.typeletter(self.typestring[self.typepos]);
            self.typepos=self.typepos+1;
        return;
    def typeletter(self,key):
        """Type a letter on IN3.  Zero for keyup."""
        #if type(key)==str: key=ord(key);
        #Send a key-up.
        self.wreg(rEP3INFIFO,0);
        self.wreg(rEP3INFIFO,0);
        self.wreg(rEP3INFIFO,self.asc2hid(key));
        self.wreg(rEP3INBC,3);
    def do_IN3(self):
        """Handle IN3 event."""
        #Don't bother clearing interrupt flag, that's done by sending the reply.
        self.type_IN3();
        
