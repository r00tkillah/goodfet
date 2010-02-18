#!/usr/bin/env python
# GoodFET Chipcon Example
#                                                                                                                                          
# (C) 2009 Travis Goodspeed <travis at radiantmachines.com>
#                                                                                                                                          
# This code is being rewritten and refactored.  You've been warned!                                                                                                                

import sys;
import binascii;

sys.path.append('/Users/travis/svn/goodfet/trunk/client/')

from GoodFETCC import GoodFETCC;
from intelhex import IntelHex16bit, IntelHex;


client=GoodFETCC();
client.serInit();

client.setup();
client.start();

bytecount=0;
lastcount=0;

bytescount=64;
bytestart=0x0C;

bytes=[];

f="random.bin"; #sys.argv[1];
file = open(f, mode='wb')

print "Writing random data to %s" % f;

#while bytecount<0x20000:
while 1:
    client.CChaltcpu();
    
    randcode=client.CCpeekiramword(0x08);
    randcount=client.CCpeekiramword(0x0A);
    byte=0;
    
    if randcount!=lastcount and randcode==0xbeef:
        #New bytes are ready, halted in steady state.
        lastcount=randcount;
        sum=0;
        for a in range(bytestart,bytestart+bytescount):
            byte=client.CCpeekirambyte(a);
            file.write(chr(byte));
            file.flush();
            sum=sum+byte;
#         print "Got 0x%06x bytes." % bytescount;
#         print "%04x %04x: %02x%02x..." % (
#             client.CCpeekiramword(0x08),
#             client.CCpeekiramword(0x0a),
#             client.CCpeekirambyte(0x0C),
#             client.CCpeekirambyte(0x0d));
        print "%02x: %010i" % (byte,sum);
        sys.stdout.flush();
    client.CCreleasecpu();

file.close();

