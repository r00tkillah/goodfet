#!/usr/bin/env python
# GoodFET Client Library
# 
# (C) 2009 Travis Goodspeed <travis at radiantmachines.com>
#
# This code is being rewritten and refactored.  You've been warned!

import sys, os;
import binascii;

from GoodFET import GoodFET;
from intelhex import IntelHex;

class GoodFETConsole():
    """An interactive goodfet driver."""
    
    def __init__(self, client):
        self.client=client;
        client.serInit();
        client.setup();
        client.start();
    def handle(self, str):
        """Handle a command string.  First word is command."""
        #Lines beginning with # are comments.
        if(str[0]=="#"):  return;
        #Lines beginning with ! are Python.
        if(str[0]=="!"):
            try:
                exec(str.lstrip('!'));
            except:
                print sys.exc_info()[0];
            return;
        #Backtick (`) indicates shell commands.
        if(str[0]=='`'):
            os.system(str.lstrip('`'));
            return;
        #By this point, we're looking at a GoodFET command.
        args=str.split();
        if len(args)==0:
            return;
        try:
            eval("self.CMD%s(args)" % args[0])
        except:
            print sys.exc_info()[0];
            #print "Unknown command '%s'." % args[0];
    def CMDinfo(self,args):
        print self.client.infostring()
    def CMDlock(self,args):
        print "Locking.";
        self.client.lock();
    def CMDerase(self,args):
        print "Erasing.";
        self.client.erase();
    def CMDtest(self,args):
        self.client.test();
        return;
    def CMDstatus(self,args):
        print self.client.status();
        return;
    def CMDpeek(self,args):
        adr=eval(args[1]);
        memory="vn";
        if(len(args)>2):
            memory=args[2];
        print "0x%08x:= 0x%04x" % (adr, self.client.peek16(adr,memory));
    def CMDflash(self,args):
        file=args[1];
        self.client.flash(self.expandfilename(file));
    def expandfilename(self,filename):
        if(filename[0]=='~'):
            return "%s%s" % (os.environ.get("HOME"),filename.lstrip('~'));
        return filename;
    
    
