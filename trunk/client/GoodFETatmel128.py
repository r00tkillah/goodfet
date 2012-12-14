# GoodFET client to interface zigduino/atmel128 radio
# forked by bx from code by neighbor Travis Goodspeed
from GoodFETAVR import GoodFETAVR
import sys, binascii, os, array, time, glob, struct

fmt = ("B", "<H", None, "<L")

class GoodFETatmel128rfa1(GoodFETAVR):
    ATMELRADIOAPP = 0x53
    def pyserInit(self, port, timeout, attemptlimit):
        """Open the serial port"""
        # Make timeout None to wait forever, 0 for non-blocking mode.
        import serial;

        if os.name=='nt' and sys.version.find('64 bit')!=-1:
            print "WARNING: PySerial requires a 32-bit Python build in Windows.";

        if port is None and os.environ.get("GOODFET")!=None:
            glob_list = glob.glob(os.environ.get("GOODFET"));
            if len(glob_list) > 0:
                port = glob_list[0];
            else:
                port = os.environ.get("GOODFET");
        if port is None:
            glob_list = glob.glob("/dev/tty.usbserial*");
            if len(glob_list) > 0:
                port = glob_list[0];
        if port is None:
            glob_list = glob.glob("/dev/ttyUSB*");
            if len(glob_list) > 0:
                port = glob_list[0];
        if port is None:
            glob_list = glob.glob("/dev/ttyU0");
            if len(glob_list) > 0:
                port = glob_list[0];
        if port is None and os.name=='nt':
            from scanwin32 import winScan;
            scan=winScan();
            for order,comport,desc,hwid in sorted(scan.comports()):
                try:
                    if hwid.index('FTDI')==0:
                        port=comport;
                        #print "Using FTDI port %s" % port
                except:
                    #Do nothing.
                    a=1;

        baud=115200;
        self.serialport = serial.Serial(
            port,
            baud,
            parity = serial.PARITY_NONE,
            timeout=timeout
            )

        self.verb=0;
        self.data=""
        attempts=0;
        connected=0;

        while connected==0:
            while self.verb!=0x7F or self.data!="http://goodfet.sf.net/":
                if attemptlimit is not None and attempts >= attemptlimit:
                    return
                elif attempts==2 and os.environ.get("board")!='telosb':
                    print "See the GoodFET FAQ about missing info flash.";
                    self.serialport.setTimeout(0.2);
                    #Explicitly set RTS and DTR to halt board.
                    self.serialport.setRTS(1);
                    self.serialport.setDTR(1);
                    #Drop DTR, which is !RST, low to begin the app.
                    self.serialport.setDTR(0);

                attempts=attempts+1;
                self.readcmd(); #Read the first command.
                if self.verbose:
                    print "Got %02x,%02x:'%s'" % (self.app,self.verb,self.data);

            #Here we have a connection, but maybe not a good one.
            #print "We have a connection."
            for foo in range(1,30):
                time.sleep(1)
                if not self.monitorecho():
                    connected = 0
                    if self.verbose:
                        print "Comm error on try %i." % (foo)
                else:
                    connected = 1
                    break
        if self.verbose:
            print "Connected after %02i attempts." % attempts;
        self.serialport.setTimeout(12);


    def writecmd(self, app, verb, count=0, data=[]):
        """Write a command and some data to the GoodFET."""
        self.serialport.write(chr(app));
        self.serialport.write(chr(verb));

        if count > 0:
            if(isinstance(data,list)):
                old = data
                data = []
                for i in range(0,count):
                    data += chr(old[i]);
            outstr=''.join(data);

        #little endian 16-bit length
            count = len(outstr)
            self.serialport.write(chr(count&0xFF));
            self.serialport.write(chr(count>>8));
            if self.verbose:
                print "Tx: ( 0x%02x, 0x%02x, %d )" % ( app, verb, count )
                print "sending: %s" %outstr.encode("hex")

            self.serialport.write(outstr);
        else: # count == 0
            self.serialport.write("\x00")
            self.serialport.write("\x00")

        if not self.besilent:
            out = self.readcmd()
            #if out:
            #    print "read: " + out
            return out
        else:
            return []

    def readcmd(self):
        """Read a reply from the GoodFET."""
        app = self.serialport.read(1)
        if len(app) < 1:
            self.app = 0
            self.verb = 0
            self.count = 0
            self.data = ""
            return

        self.app=ord(app);
        self.verb=ord(self.serialport.read(1));

        self.count= ord(self.serialport.read(1)) + (ord(self.serialport.read(1))<<8)

        if self.verbose:
            print "Rx: ( 0x%02x, 0x%02x, %i )" % ( self.app, self.verb, self.count )

        #Debugging string; print, but wait.
        if self.app==0xFF:
            if self.verb==0xFF:
                print "# DEBUG %s" % self.serialport.read(self.count)
            elif self.verb==0xFE:
                print "# DEBUG 0x%x" % struct.unpack(fmt[self.count-1], self.serialport.read(self.count))[0]
            elif self.verb==0xFD:
                        #Do nothing, just wait so there's no timeout.
                print "# NOP.";
            return ""
        else:
            self.data=self.serialport.read(self.count);
            return self.data;

    def RF_setchannel(self, chan):
        if (chan < 11) or (chan > 26):
            print "Channel out of range"
        else:
            self.poke(0x8, chan)

    def peek(self,reg,bytes=-1):
        """Read a Register. """
        #Automatically calibrate the len.
        if bytes==-1:
            bytes=1;
            #if reg==0x0a or reg==0x0b or reg==0x10: bytes=5;
        data = [reg, 0, bytes%255, bytes>>8] + ([0]*bytes)
        self.writecmd(self.ATMELRADIOAPP,0x02,len(data),data);
        toret=0;
        #print self.data.encode("hex")
        if self.data:
            #for i in range(0,bytes):
            #    toret=toret|(ord(self.data[i+1])<<(8*i));
            #return toret;
            # right now only works with a byte of data
            return ord(self.data)
        else:
            return -1

    def poke(self,reg,val,bytes=-1):
        """Write an Register."""
        data=[reg, 0]

        #Automatically calibrate the len.
        if bytes==-1:
            bytes=1;
            #if reg==0x0a or reg==0x0b or reg==0x10: bytes=5;
        for i in range(0,bytes):
            data=data+[(val>>(8*i))&0xFF];

        self.writecmd(self.ATMELRADIOAPP,0x03,len(data),data);
        if self.peek(reg,bytes)!=val:
            print "Warning, failed to set r%02x=%02x, got %02x." %(
                reg,
                val,
                self.peek(reg,bytes));

        return;


    def RF_setup(self):
        self.writecmd(self.ATMELRADIOAPP, 0x10, 0, None)

    def RF_rxpacket(self):
        """Get a packet from the radio.  Returns None if none is waiting."""
        #doto: check if packet has arrived, flush if not new
        self.writecmd(self.ATMELRADIOAPP, 0x80, 0, None)
        data=self.data;
        self.packetlen = len(data)
        if (self.packetlen > 0):
            return data;
        else:
            return None

    def RX_txpacket(self, payload):
        self.writecmd(self.ATMELRADIOAPP, 0x81, len(payload)+1,chr(len(payload))+payload)
