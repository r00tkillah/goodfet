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
    """ 
    This class provides methods for reverse-engineering the protocols on the CAN bus network
    via the GOODTHOPTER10 board, U{http://goodfet.sourceforge.net/hardware/goodthopter10/}    
    
    """
    
    def __init__(self, datalocation):
        """ 
        Constructor
        @type datalocation: string
        @param datalocation: path to the folder where data will be stored
        """
        GoodFETMCPCANCommunication.__init__(self, location)
        #super(experiments,self).__init(self)
        self.freq = 500;
        
    
    def filterStdSweep(self, freq, low, high, time = 5):
        """
        This method will sweep through the range of standard ids given from low to high.
        This will actively filter for 6 ids at a time and sniff for the given amount of
        time in seconds. If at least one message is read in then it will go individually
        through the 6 ids and sniff only for that id for the given amount of time. All the
        data gathered will be saved. 
        
        @type  freq: number
        @param freq: The frequency at which the bus is communicating
        @type   low: integer
        @param  low: The low end of the id sweep
        @type  high: integer 
        @param high: The high end of the id sweep
        @type  time: number
        @param time: Sniff time for each trial. Default is 5 seconds
        
        @rtype: list of numbers
        @return: A list of all IDs found during the sweep.
        """
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
    
    
    def sweepRandom(self, freq, number = 5, time = 5):
        """
        This method will choose random values to listen out of all the possible standard ids up to
        the given number. It will sniff for the given amount of time on each set of ids on the given 
        frequency. Sniffs in groups of 6 but when at least one message is read in it will go through all
        six individually before continuing.
        
        @type  freq: number
        @param freq: The frequency at which the bus is communicating
        @type  number: integer
        @param number: High end of the possible ids. This will define a range from 0 to number that the ids will be chosen from
        @type  time: number
        @param time: Sniff time for each trial. Default is 5 seconds
        
        @rtype: list of numbers, list of numbers 
        @return: A list of all IDs found during the sweep and a list of all the IDs that were listened for throughout the test
        """
        msgIDs = [] #standard IDs that we have observed during run
        ids = [] #standard IDs that have been tried
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
            #print comment
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
    
    
    def rtrSweep(self,freq,lowID,highID, attempts = 1,duration = 1, verbose = True):
        """
        This method will sweep through the range of ids given by lowID to highID and
        send a remote transmissions request (RTR) to each id and then listen for a response. 
        The RTR will be repeated in the given number of attempts and will sniff for the given duration
        continuing to the next id.
        
        @type  freq: number
        @param freq: The frequency at which the bus is communicating
        @type   lowID: integer
        @param  lowID: The low end of the id sweep
        @type  highID: integer 
        @param highID: The high end of the id sweep
        @type attempts: integer
        @param attempts: The number of times a RTR will be repeated for a given standard id
        @type  duration: integer
        @param duration: The length of time that it will listen to the bus after sending an RTR
        @type verbose:  boolean
        @param verbose: When true, messages will be printed out to the terminal
        
        @rtype: None
        @return: Does not return anything
        """
        #set up file for writing
        now = datetime.datetime.now()
        datestr = now.strftime("%Y%m%d")
        path = self.DATA_LOCATION+datestr+"_rtr.csv"
        filename = path
        outfile = open(filename,'a');
        dataWriter = csv.writer(outfile,delimiter=',');
        dataWriter.writerow(['# Time     Error        Bytes 1-13']);
        dataWriter.writerow(['#' + "rtr sweep from %d to %d"%(lowID,highID)])
        if( verbose):
            print "started"
        #self.client.serInit()
        #self.spitSetup(freq)
        
        #for each id
        for i in range(lowID,highID+1, 1):
            self.client.serInit()
            self.spitSetup(freq) #reset the chip to try and avoid serial timeouts
            #set filters
            standardid = [i, i, i, i]
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
            while ((time.time() - starttime) < duration): #listen for the given duration time period
                packet = self.client.rxpacket()
                if( packet == None):
                    continue
                # we have sniffed a packet, save it
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
            trial= 2;
            # for each trial repeat
            while( trial <= attempts):
                print "trial: ", trial
                self.client.MCPrts(TXB0=True);
                starttime = time.time()
                # this time we will sniff for the given amount of time to see if there is a
                # time till the packets come in
                while( (time.time()-starttime) < duration):
                    packet=self.client.rxpacket();
                    if( packet == None):
                        continue
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
    def generationFuzzer(self,freq, standardIDs, dbLimits, period, writesPerFuzz, Fuzzes):
        """
        This method will perform generation based fuzzing on the bus. The method will inject
        properly formatted, randomly generated messages at a given period for a I{writesPerFuzz} 
        number of times. The packets that are injected into the bus will all be saved in the following path
        DATALOCATION/InjectedData/(today's date (YYYYMMDD))_GenerationFuzzedPackets.csv. An example filename would be 20130222_GenerationFuzzedPackets.csv
        Where DATALOCATION is provided when the class is initiated. The data will be saved as integers.
        Each row will be formatted in the following form::
                     row = [time of injection, standardID, 8, db0, db1, db2, db3, db4, db5, db6, db7]
        
        @type  freq: number
        @param freq: The frequency at which the bus is communicating
        @type standardIDs: list of integers
        @param standardIDs: List of standard IDs the user wishes to fuzz on. An ID will randomly be chosen
                            with every new random packet generated. If only 1 ID is input in the list then it will
                            only fuzz on that one ID.
        @type  dbLimits: dictionary
        @param dbLimits: This is a dictionary that holds the limits of each bytes values. Each value in the dictionary will be a list 
                         containing the lowest possible value for the byte and the highest possible value. The form is shown below::
                            
                            dbLimits['db0'] = [low, high]
                            dbLimits['db1'] = [low, high]
                            ...
                            dbLimits['db7'] = [low, high] 
        
        @type period: number
        @param period: The time gap between packet inejctions given in milliseconds
        @type writesPerFuzz: integer
        @param writesPerFuzz: This will be the number of times that each randomly generated packet will be injected onto the bus
                              before a new packet is generated
        @type Fuzzes: integer
        @param Fuzzes: The number of packets to be generated and injected onto bus
        
        @rtype: None
        @return: This method does not return anything
                         
        """
        print "Fuzzing on standard ID: %d" %standardId
        self.client.serInit()
        self.spitSetup(freq)
        packet = [0,0,0,0,0,0,0,0,0,0,0,0] #empty template
        #form a basic packet
        
#        #### split SID into different regs
#        SIDlow = (standardIds[0] & 0x07) << 5;  # get SID bits 2:0, rotate them to bits 7:5
#        SIDhigh = (standardIds[0] >> 3) & 0xFF; # get SID bits 10:3, rotate them to bits 7:0
#        
#        packet = [SIDhigh, SIDlow, 0x00,0x00, # pad out EID regs
#                  0x08, # bit 6 must be set to 0 for data frame (1 for RTR) 
#                  # lower nibble is DLC                   
#                 packetTemp[0],packetTemp[1],packetTemp[2],packetTemp[3],packetTemp[4],packetTemp[5],packetTemp[6],packetTemp[7]]
#        
        
        #get folder information (based on today's date)
        now = datetime.datetime.now()
        datestr = now.strftime("%Y%m%d")
        path = self.DATA_LOCATION+"InjectedData/"+datestr+"_GenerationFuzzedPackets.csv"
        filename = path
        outfile = open(filename,'a');
        dataWriter = csv.writer(outfile,delimiter=',');
        #dataWriter.writerow(['# Time     Error        Bytes 1-13']);
        #dataWriter.writerow(['#' + description])
            
        numIds = len(standardIDs)
        fuzzNumber = 0; #: counts the number of packets we have generated
        while( fuzzNumber < Fuzzes):
            id_new = standsardIDs[random.randint(0,numIds-1)]
            #### split SID into different regs
            SIDhigh = (id_new >> 3) & 0xFF; # get SID bits 10:3, rotate them to bits 7:0
            SIDlow = (id_new & 0x07) << 5;  # get SID bits 2:0, rotate them to bits 7:5
            packet[0] = SIDhigh
            packet[1] = SIDlow
            
            #generate a fuzzed packet
            for i in range(0,8): # for each data byte, fuzz it
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
            time.sleep(period/1000)
            
            #inject the packet the given number of times. 
            for i in range(1,writesPerFuzz):
                self.client.MCPrts(TXB0=True)
                time.sleep(period/1000)
            fuzzNumber += 1
        print "Fuzzing Complete"   
        outfile.close()
            
    
#    def generationFuzzRandomID(self, freq, standardIDs, dbLimits, period, writesPerFuzz, Fuzzes):
#        print "Fuzzing on standard ID: %d" %standardId
#        self.client.serInit()
#        self.spitSetup(freq)
#        packetTemp = [0,0,0,0,0,0,0,0]
#        #form a basic packet
#        
#        #### split SID into different regs
#        SIDlow = (standardId & 0x07) << 5;  # get SID bits 2:0, rotate them to bits 7:5
#        SIDhigh = (standardId >> 3) & 0xFF; # get SID bits 10:3, rotate them to bits 7:0
#        
#        packet = [SIDhigh, SIDlow, 0x00,0x00, # pad out EID regs
#                  0x08, # bit 6 must be set to 0 for data frame (1 for RTR) 
#                  # lower nibble is DLC                   
#                 packetTemp[0],packetTemp[1],packetTemp[2],packetTemp[3],packetTemp[4],packetTemp[5],packetTemp[6],packetTemp[7]]
#        
#        
#        #get folder information (based on today's date)
#        now = datetime.datetime.now()
#        datestr = now.strftime("%Y%m%d")
#        path = self.DATA_LOCATION+"InjectedData/"+datestr+"_GenerationFuzzedPackets.csv"
#        filename = path
#        outfile = open(filename,'a');
#        dataWriter = csv.writer(outfile,delimiter=',');
#        #dataWriter.writerow(['# Time     Error        Bytes 1-13']);
#        #dataWriter.writerow(['#' + description])
#            
#        numIds = len(standardIDs)
#        fuzzNumber = 0;
#        while( fuzzNumber < Fuzzes):
#            id_new = standsardIDs[random.randint(0,numIds-1)]
#            #### split SID into different regs
#            SIDlow = (id_new & 0x07) << 5;  # get SID bits 2:0, rotate them to bits 7:5
#            SIDhigh = (id_new >> 3) & 0xFF; # get SID bits 10:3, rotate them to bits 7:0
#            packet[0] = SIDhigh
#            packet[1] = SIDlow
#            
#            #generate a fuzzed packet
#            for i in range(0,8): # for each databyte, fuzz it
#                idx = "db%d"%i
#                limits = dbLimits[idx]
#                value = random.randint(limits[0],limits[1]) #generate pseudo-random integer value
#                packet[i+5] = value
#            
#            #put a rough time stamp on the data and get all the data bytes    
#            row = [time.time(), standardId,8]
#            msg = "Injecting: "
#            for i in range(5,13):
#                row.append(packet[i])
#                msg += " %d"%packet[i]
#            #print msg
#            dataWriter.writerow(row)
#            self.client.txpacket(packet)
#            #inject the packet repeatily 
#            for i in range(1,writesPerFuzz):
#                self.client.MCPrts(TXB0=True)
#                time.sleep(period/1000)
#            fuzzNumber += 1
#        print "Fuzzing Complete"   
#        outfile.close()