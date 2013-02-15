import sys;
import binascii;
import array;
import csv, time, argparse;
import datetime
import os
from random import randrange
import random
from GoodFETMCPCAN import GoodFETMCPCAN;
from GoodFETMCPCANCommunication import GoodFETMCPCANCommunication
from intelhex import IntelHex;
import Queue
import math

tT = time


class experiments(GoodFETMCPCANCommunication):
    
    def __init__(self):
        GoodFETMCPCANCommunication.__init__(self)
        #super(experiments,self).__init(self)
        self.freq = 500;
        
    def filterStdSweep(self, freq, low, high, time = 5):
        msgIDs = []
        self.client.serInit()
        self.client.MCPsetup()
        for i in range(low, high+1, 6):
            print "sniffing id: %d, %d, %d, %d, %d, %d" % (i,i+1,i+2,i+3,i+4,i+5)
            comment= "sweepFilter: "
            #comment = "sweepFilter_%d_%d_%d_%d_%d_%d" % (i,i+1,i+2,i+3,i+4,i+5)
            description = "Running a sweep filer for all the possible standard IDs. This run filters for: %d, %d, %d, %d, %d, %d" % (i,i+1,i+2,i+3,i+4,i+5)
            count = self.sniff(freq=freq, duration = time, description = description,comment = comment, standardid = [i, i+1, i+2, i+3, i+4, i+5])
            if( count != 0):
                for j in range(i,i+5):
                    comment = "sweepFilter: "
                    #comment = "sweepFilter: %d" % (j)
                    description = "Running a sweep filer for all the possible standard IDs. This run filters for: %d " % j
                    count = self.sniff(freq=freq, duration = time, description = description,comment = comment, standardid = [j, j, j, j])
                    if( count != 0):
                        msgIDs.append(j)
        return msgIDs
    
    
    def sweepRandom(self, freq, number = 5, time = 200):
        msgIDs = []
        ids = []
        self.client.serInit()
        self.client.MCPsetup()
        for i in range(0,number+1,6):
            idsTemp = []
            comment = "sweepFilter: "
            for j in range(0,6,1):
                id = randrange(2047)
                #comment += "_%d" % id
                idsTemp.append(id)
                ids.append(id)
            print comment
            description = "Running a sweep filer for all the possible standard IDs. This runs the following : " + comment
            count = self.sniff(freq=freq, duration=time, description=description, comment = comment, standardid = idsTemp)
            if( count != 0):
                for element in idsTemp:
                    #comment = "sweepFilter: %d" % (element)
                    comment="sweepFilter: "
                    description = "Running a sweep filer for all the possible standard IDs. This run filters for: %d " % element
                    count = self.sniff(freq=freq, duration = time, description = description,comment = comment, standardid = [element, element, element])
                    if( count != 0):
                        msgIDs.append(j)
        return msgIDs, ids
    
    
     # this will sweep through the given ids to request a packet and then sniff on that
    # id for a given amount duration. This will be repeated the number of attempts time
    
    #at the moment this is set to switch to the next id once  a message is identified
    def rtrSweep(self,freq,lowID,highID, attempts = 1,duration = 1, verbose = True):
        #set up file
        now = datetime.datetime.now()
        datestr = now.strftime("%Y%m%d")
        path = self.DATALOCATION+datestr+"_rtr.csv"
        filename = path
        outfile = open(filename,'a');
        dataWriter = csv.writer(outfile,delimiter=',');
        dataWriter.writerow(['# Time     Error        Bytes 1-13']);
        dataWriter.writerow(['#' + "rtr sweep from %d to %d"%(lowID,highID)])
        print "started"
        #self.client.serInit()
        #self.spitSetup(freq)
        for i in range(lowID,highID+1, 1):
            self.client.serInit()
            self.spitSetup(freq)
            standardid = [i, i, i, i]
            #set filters
            self.addFilter(standardid, verbose = True)
            
            #### split SID into different areas
            SIDlow = (standardid[0] & 0x07) << 5;  # get SID bits 2:0, rotate them to bits 7:5
            SIDhigh = (standardid[0] >> 3) & 0xFF; # get SID bits 10:3, rotate them to bits 7:0
            #create RTR packet
            packet = [SIDhigh, SIDlow, 0x00,0x00,0x40]
            dataWriter.writerow(["#requested id %d"%i])
            #self.client.poke8(0x2C,0x00);  #clear the CANINTF register; we care about bits 0 and 1 (RXnIF flags) which indicate a message is being held 
            #clear buffer
            packet1 = self.client.rxpacket();
            packet2 = self.client.rxpacket();
            #send in rtr request
            self.client.txpacket(packet)
            ## listen for 2 packets. one should be the rtr we requested the other should be
            ## a new packet response
            starttime = time.time()
            while ((time.time() - starttime) < duration):
                packet = self.client.rxpacket()
                if( packet == None):
                    continue
                row = []
                row.append("%f"%time.time()) #timestamp
                row.append(0) #error flag (not checkign)
                row.append("rtrRequest_%d"%i) #comment
                row.append(duration) #sniff time
                row.append(1) # filtering boolean
                for byte in packet:
                    row.append("%02x"%ord(byte));
                dataWriter.writerow(row)
                print self.client.packet2parsedstr(packet)
#            packet1=self.client.rxpacket();
#            packet2=self.client.rxpacket();
#            if( packet1 != None and packet2 != None):
#                print "packets recieved :\n "
#                print self.client.packet2parsedstr(packet1);
#                print self.client.packet2parsedstr(packet2);
#                continue
#            elif( packet1 != None):
#                print self.client.packet2parsedstr(packet1)
#            elif( packet2 != None):
#                print self.client.packet2parsedstr(packet2)
            trial= 2;
            # for each trial
            while( trial <= attempts):
                print "trial: ", trial
                self.client.MCPrts(TXB0=True);
                starttime = time.time()
                # this time we will sniff for the given amount of time to see if there is a
                # time till the packets come in
                while( (time.time()-starttime) < duration):
                    packet=self.client.rxpacket();
                    row = []
                    row.append("%f"%time.time()) #timestamp
                    row.append(0) #error flag (not checking)
                    row.append("rtrRequest_%d"%i) #comment
                    row.append(duration) #sniff time
                    row.append(1) # filtering boolean
                    for byte in packet:
                        row.append("%02x"%ord(byte));
                    dataWriter.writerow(row)
                    print self.client.packet2parsedstr(packet)
#                    packet2=self.client.rxpacket();
#                    
#                    if( packet1 != None and packet2 != None):
#                        print "packets recieved :\n "
#                        print self.client.packet2parsedstr(packet1);
#                        print self.client.packet2parsedstr(packet2);
#                        #break
#                    elif( packet1 != None):
#                        print "just packet1"
#                        print self.client.packet2parsedstr(packet1)
#                    elif( packet2 != None):
#                        print "just packet2"
#                        print self.client.packet2parsedstr(packet2)
                trial += 1
        print "sweep complete"
        outfile.close()
        
    # This method will do generation based fuzzing on the id given in standard id
    # dbLimits is a dictionary of the databytes
    # dbLimits['db0'] = [low, High]
    # ..
    # dbLimits['db7'] = [low, High]
    # where low is the low end of values for the fuzz, high is the high end value
    # period is the time between sending packets in milliseconds, writesPerFuzz is the times the 
    # same fuzzed packet will be injecetez. Fuzzes is the number of different packets to be injected
    def generationFuzzer(self,freq, standardId, dbLimits, period, writesPerFuzz, Fuzzes):
        print "Fuzzing on standard ID: %d" %standardId
        self.client.serInit()
        self.spitSetup(freq)
        packetTemp = [0,0,0,0,0,0,0,0]
        #form a basic packet
        
        #### split SID into different regs
        SIDlow = (standardId & 0x07) << 5;  # get SID bits 2:0, rotate them to bits 7:5
        SIDhigh = (standardId >> 3) & 0xFF; # get SID bits 10:3, rotate them to bits 7:0
        
        packet = [SIDhigh, SIDlow, 0x00,0x00, # pad out EID regs
                  0x08, # bit 6 must be set to 0 for data frame (1 for RTR) 
                  # lower nibble is DLC                   
                 packetTemp[0],packetTemp[1],packetTemp[2],packetTemp[3],packetTemp[4],packetTemp[5],packetTemp[6],packetTemp[7]]
        
        
        #get folder information (based on today's date)
        now = datetime.datetime.now()
        datestr = now.strftime("%Y%m%d")
        path = self.DATALOCATION+"InjectedData/"+datestr+"_GenerationFuzzedPackets.csv"
        filename = path
        outfile = open(filename,'a');
        dataWriter = csv.writer(outfile,delimiter=',');
        #dataWriter.writerow(['# Time     Error        Bytes 1-13']);
        #dataWriter.writerow(['#' + description])
            
        
        fuzzNumber = 0;
        while( fuzzNumber < Fuzzes):
            #generate a fuzzed packet
            for i in range(0,8): # for each databyte, fuzz it
                idx = "db%d"%i
                limits = dbLimits[idx]
                value = random.randint(limits[0],limits[1]) #generate pseudo-random integer value
                packet[i+5] = value
            
            #put a rough time stamp on the data and get all the data bytes    
            row = [time.time(), standardId,8]
            msg = "Injecting: "
            for i in range(5,13):
                row.append(packet[i])
                msg += " %d"%packet[i]
            #print msg
            dataWriter.writerow(row)
            self.client.txpacket(packet)
            #inject the packet repeatily 
            for i in range(1,writesPerFuzz):
                self.client.MCPrts(TXB0=True)
                time.sleep(period/1000)
            fuzzNumber += 1
            
        outfile.close()
            
    
    
    
