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

tT = time
class FordExperiments(GoodFETMCPCANCommunication, dataLocation):
    
    def __init__(self):
        GoodFETMCPCANCommunication.__init__(self, dataLocation)
        #super(FordExperiments,self).__init__(self) #initialize chip
        self.freq = 500;

    def mimic1056(self,packetData,runTime):
        #setup chip
        self.client.serInit()
        self.spitSetup(self.freq)
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
            
                
         
    def cycledb1_1056(self,runTime):
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
            time.sleep(.1)
            packet1 = self.client.rxpacket()
            if(packet1 != None):
                packetParsed = self.client.packet2parsed(packet1)
        recieveTime = time.time()
        packetParsed = self.client.packet2parsed(packet1)
        if( packetParsed['sID'] != 1056):
            print "Sniffed wrong packet"
            return
        packet = []
        #set data packet to match what was sniffed or at least what was input
        for i in range(0,8):
            idx = "db%d"%i
            packet.append(ord(packetParsed.get(idx)))
        packetValue = 0
        packet[1] = packetValue;
        
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
            packetValue += 10
            pV = packetValue%255
            #temp = ((packetValue+1))%2
            #if( temp == 1):
            #    pV = packetValue%255
            #else:
            #    pV = 0
            packet[6] = pV
            #packet[6] = 1
            print packet
            self.client.txpacket(packet)
            packetCount += 1
            tpast = time.time()  #update our transmit time on the one before   
        print packetCount;
        
    def getBackground(self,sId):
        packet1 = self.client.rxpacket();
        if(packet1 != None):
            packetParsed = self.client.packet2parsed(packet1);
        #keep sniffing till we read a packet
        while( packet1 == None or packetParsed.get('sID') != sId ):
            packet1 = self.client.rxpacket()
            if(packet1 != None):
                packetParsed = self.client.packet2parsed(packet1)
            
        #recieveTime = time.time()
        return packetParsed

    def cycle4packets1279(self):
        self.client.serInit()
        self.spitSetup(500)
        # filter on 1279
        self.addFilter([1279, 1279, 1279, 1279, 1279, 1279], verbose = False)
        packetParsed = self.getBackground(1279)
        packet = []
        if (packetParsed[db0] == 16):
            # if it's the first of the four packets, replace the value in db7  with 83
            packetParsed[db7] = 83
            # transmit new packet
            self.client.txpacket(packetParsed)
        else:
        # otherwise, leave it alone
            # transmit same pakcet we read in
            self.client.txpacket(packetParsed)
        # print the packet we are transmitting
        print packetParsed
        
        
    def oscillateTemperature(self,time):
        #setup chip
        self.client.serInit()
        self.spitSetup(500)
        #FIGURE out how to clear buffers
        self.addFilter([1056, 1056, 1056, 1056,1056, 1056], verbose=False)
        packetParsed = self.getBackground(1056)
        packet = []
        #set data packet to match what was sniffed or at least what was input
        for i in range(0,8):
            idx = "db%d"%i
            packet.append(ord(packetParsed.get(idx)))
        packetValue = 0
        packet[1] = packetValue;
        
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
        startTime = tT.time()
        while( (tT.time()-startTime) < runTime):
            dt = tT.time()-startTime
            inputValue = ((2.0*math.pi)/20.0)*dt
            value = 30*math.sin(inputValue)+130
            print value
            #packet[5] = int(value)
            if( value > 130 ):
                packet[5] = 160
            else:
                packet[5] = 100
            #packet[6] = 1
            print packet
            self.client.txpacket(packet)
            packetCount += 1
            #tpast = time.time()  #update our transmit time on the one before   
        print packetCount;
        
        
if __name__ == "__main__":
    fe = FordExperiments();
    packetData = {}
    packetData['db4'] = 4;
    runTime = 100;
    #fe.mimic1056(packetData, runTime)
    #fe.cycledb1_1056(runTime)
    fe.oscillateTemperature(runTime)
