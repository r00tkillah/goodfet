import sys;
import binascii;
import array;
import csv, time, argparse;
import datetime
import os
from random import randrange
from GoodFETMCPCAN import GoodFETMCPCAN;
from GoodFETMCPCANCommunication import GoodFETMCPCANCommunication
from intelhex import IntelHex;
import Queue
import math

class FordExperiments(GoodFETMCPCANCommunication):
    
    def init(self):
        super(FordExperimetns,self).__init__(self) #initialize chip
        self.freq = 500;

    def mimic1056(self,packetData,runTime):
        #setup chip
        self.client.serInit()
        self.spitSetup(500)
        #FIGURE out how to clear buffers
        self.addFilter([1056, 1056, 1056, 1056,1056, 1056], verbose=False)
        packet1 = self.client.rxpacket();
        if(packet1 != None):
            packetParsed = self.client.packet2parsed(packet1);
        #keep sniffing till we read a packet
        while( packet1 == None or packetParsed.get('sID') != 1056 ):
            packet1 = self.client.rxpacket()
            if(packet1 != None):
                packetParsed = self.client.packet2parsed(packet1)
        recieveTime = time.time()
        packetParsed = self.client.packet2parsed(packet1)
        if( packetParsed['sID'] != 1056):
            print "Sniffed wrong packet"
            return
        countInitial = ord(packetParsed['db3']) #initial count value
        packet = []
        #set data packet to match what was sniffed or at least what was input
        for i in range(0,8):
            idx = "db%d"%i
            if(packetData.get(idx) == None):
                packet.append(ord(packetParsed.get(idx)))
            else:
                packet.append(packetData.get(idx))
        print packet
        #### split SID into different regs
        SIDlow = (1056 & 0x07) << 5;  # get SID bits 2:0, rotate them to bits 7:5
        SIDhigh = (1056 >> 3) & 0xFF; # get SID bits 10:3, rotate them to bits 7:0
        packet = [SIDhigh, SIDlow, 0x00,0x00, # pad out EID regs
                  0x08, # bit 6 must be set to 0 for data frame (1 for RTR) 
                  # lower nibble is DLC                   
                 packet[0],packet[1],packet[2],packet[3],packet[4],packet[5],packet[6],packet[7]]
        packetCount = 1;
        self.client.txpacket(packet);
        tpast = time.time()
        while( (time.time()-recieveTime) < runTime):
            #care about db3 or packet[8] that we want to count at the rate that it is
            dT = time.time()-tpast
            if( dT/0.2 >= 1):
                db3 = (countInitial + math.floor((time.time()-recieveTime)/0.2))%255
                packet[8] = db3
                self.client.txpacket(packet)
                packetCount += 1
            else:
                packetCount += 1
                self.client.MCPrts(TXB0=True)
            tpast = time.time()  #update our transmit time on the one before   
            
                
         


if __name__ == "__main__":
    fe = FordExperiments();
    packetData = {}
    packetData['db4'] = 4;
    runTime = 10;
    fe.mimic1056(packetData, runTime)
