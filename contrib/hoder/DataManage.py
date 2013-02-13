# 
# 1/11/2012

import MySQLdb
import sys
import csv
import argparse;
import time
import struct
import glob
import os
import datetime
#data parsing assumes an standard ID!!

class DataManage:
    
    
    def __init__(self, host, db, username, password, table):
        
        # Save MYSQL information for later use
        self.host = host
        self.db = db
        self.username = username
        self.password = password
        self.table = table
        self.DATALOCATION = "../ThayerData/"
        self.SQLDDATALOCATION = self.DATALOCATION+"SQLData/"
        
    def getSQLLocation(self):
        return self.SQLDDATALOCATION
    
    def getDataLocation(self):
        return self.DATALOCATION
    
    #Creates a new MySQL table in the database with the given table name
    def createTable(self, table):
        self.table = table
        cmd = "CREATE TABLE %s (\
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,\
  `time` double(20,5) unsigned NOT NULL,\
  `stdID` int(5) unsigned NOT NULL,\
  `exID` int(5) unsigned DEFAULT NULL,\
  `length` int(1) unsigned NOT NULL,\
  `error` bit(1) NOT NULL,\
  `remoteframe` bit(1) NOT NULL DEFAULT b'0',\
  `db0` int(3) unsigned DEFAULT NULL,\
  `db1` int(3) unsigned DEFAULT NULL,\
  `db2` int(3) unsigned DEFAULT NULL,\
  `db3` int(3) unsigned DEFAULT NULL,\
  `db4` int(3) unsigned DEFAULT NULL,\
  `db5` int(3) unsigned DEFAULT NULL,\
  `db6` int(3) unsigned DEFAULT NULL,\
  `db7` int(3) unsigned DEFAULT NULL,\
  `msg` varchar(30) NOT NULL,\
  `comment` varchar(500) DEFAULT NULL,\
  `filter` bit(1) NOT NULL DEFAULT b'0',\
  `readTime` int(11) unsigned NOT NULL DEFAULT '0',\
  PRIMARY KEY (`id`)\
) ENGINE=MyISAM AUTO_INCREMENT=114278 DEFAULT CHARSET=utf8"% (table)
        self.addData(cmd)
        self.table = table
        
    def changeTable(self,table):
        self.table = table
    
    def getTable(self):
        return self.table
    
    def addData(self,cmd):
        db_conn = MySQLdb.connect(self.host, self.username, self.password, self.db)
        cursor = db_conn.cursor()
        try:
            #execute the SQL command
            cursor.execute(cmd)
            #commit the changes the to database
            db_conn.commit()
        except:
            #Rollback in case there is any error
            db_conn.rollback()
            
            #unable to add, raise an exception
            raise Exception, "Error inserting into db, %s with the command %s" % self.db,cmd
        
        db_conn.close()


    def getData(self,cmd):
        db_conn = MySQLdb.connect(self.host, self.username, self.password, self.db)
        cursor = db_conn.cursor()
        try:
            #Execute the SQL command
            cursor.execute(cmd)
            #Fetch all the rows in a list of lists.
            results = cursor.fetchall()
        except:
            error = "Error fetching data from db, %s with the command, %s" % (self.db, cmd)
            raise Exception( error )
        
        db_conn.close()
        return results
    
    # This method will take in a data packet, the time stamp, an error boolean and will add the information
    # to the MySQL table. 
    # INPUT:
    # data: list of the CAN message received. each 
    def addDataPacket(self,data,time,error):
        parse = self.parseMessage(data)
        cmd = self.getCmd(parse, time, error)
        self.addData(cmd)
       
    
    #Creates a SQl command to upload data packet to the database
    def getCmd(self,packet,time,error,duration,filter, comment=None):
        length = packet['length']
        
        cmd = "INSERT INTO %s ( time, stdID" % self.table
        
        #if there is an extended id, include it
        if(packet.get('eID')):
            cmd += ", exID"
            
        cmd +=", length,"
        
        #if there was an error detected in parsing, note it
        if( packet.get('error') != None):
            print "ERROR CHANGED"
            error = 1
        #add in only data bytes written to
        for i in range(0,length):
            cmd +=" db" + str(i) + ","
        cmd += ' error, remoteFrame'

        if( comment != None):
            cmd += ", comment"

        cmd+= ', msg, filter, readTime) VALUES (%f, %d' % (time, packet['sID'])
        
        #if there is an extended id include it
        if(packet.get('eID')):
            cmd += ", %d" % packet['eID']
        
        cmd += ", %d" % length
        
        #add data
        for i in range(0,length):
            cmd += ", %d" % (packet['db'+str(i)])
        
        cmd += ', %d, %d' %(error,packet['rtr'])

        if(comment != None):
            cmd += ',"%s"' %comment

        cmd += ', "%s", %d, %f)' %(packet['msg'], filter, duration)
         
        return cmd
    
    def writeDataCsv(self,data, filename):
        outputfile = open(filename,'a')
        dataWriter = csv.writer(outputfile,delimiter=',')
        #dataWriter.writerow(['# Time     Error        Bytes 1-13']);
        for row in data:
            rowTemp = []
            for col in row:
                if( isinstance(col,str)):
                    rowTemp.append(col)
                elif(isinstance(col,float)):
                    rowTemp.append("%f" % col)
                else:
                    rowTemp.append(col)
            dataWriter.writerow(rowTemp)
        outputfile.close()
            
    
    def writePcapUpload(self,filenameUp,filenameWriteTo):
        #load the data from the csv file
        try:
            fileObj = open(filenameUp,'rU')
            data = self.opencsv(fileObj)
        except:
            print "Unable to open file!"
            return
        self.writeToPcap(filenameWriteTo, data)
        return
        
    def writeToPcap(self,filenameWriteTo, data):
        f = open(filenameWriteTo,"wb")
        # write global header to file
        # d4c3 b2a1 0200 0400 0000 0000 0000 0000 0090 0100 be00 0000
        f.write("\xd4\xc3\xb2\xa1\x02\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x40\xe3\x00\x00\x00")
        
        # write to pcap file
        for line in data:
            # packet header creation
            ph = ''
            t = line[0]
            #get microseconds
            us = int(t*(10**6))-int(t)*(10**6);
            ph += struct.pack("<L", int(t))
            ph += struct.pack("<L", us)
            ph += struct.pack("<L", 16)
            ph += struct.pack("<L", 16)
            
            
            # write packet header
            f.write(ph)
            # create a message of characters from the integers created above
            # first 5 bytes
            msg = '%s%s%s%s%s' % (chr(line[3]), chr(line[4]), chr(line[5]), chr(line[6]), chr(line[7]))
            # 3 bytes to provide stuffing for Wireshark
            msg += '%s%s%s' % (chr(int('00', 16)), chr(int('00', 16)), chr(int('00', 16)))
            # 8 data bytes
            msg += '%s%s%s%s%s%s%s%s' % (chr(line[8]), chr(line[9]), chr(line[10]), chr(line[11]), chr(line[12]), chr(line[13]), chr(line[14]), chr(line[15]))
            # write message
            f.write(msg)
        f.close()
        
    def testSQLPCAP(self):
        cmd = 'Select time,msg from ford_2004 where comment="bgtest"'
        data = self.getData(cmd)
        self.writetoPcapfromSQL("test.pcap",data)
        return

    def writetoPcapfromSQL(self, filenameWriteto, results): # pass in results from SQL query

        f = open(filenameWriteto, "wb")
        # write global header to file
        # d4c3 b2a1 0200 0400 0000 0000 0000 0000 0090 0100 be00 0000
        f.write("\xd4\xc3\xb2\xa1\x02\x00\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x40\xe3\x00\x00\x00")
            
        # run through all lines in results
        for line in results:
            
            # create packet header for Wireshark
            ph = ''
            t = line[0]
            us = int(t*(10**6))-int(t)*(10**6) #create microseconds
            ph += struct.pack("<L", int(t)) # use time integer from results
            ph += struct.pack("<L", us) # microseconds
            ph += struct.pack("<L", 16) # number of packet octets saved in file
            ph += struct.pack("<L", 16) # packet length
            
            # write the packet header to the file
            f.write(ph)

            # create a message of characters from 'message' in SQL database
            # pad with 0s to ensure Wireshark accepts it correctly

            # separate out bytes
            bytes = [line[1][i:i+2]for i in range(0,len(line[1]),2)];
         #   print chr(int(bytes[0],16))
         #   print int(bytes[0],16)
            # first 5 bytes
            msg = '%s%s%s%s%s' % (chr(int(bytes[0], 16)), chr(int(bytes[1], 16)), chr(int(bytes[2], 16)), chr(int(bytes[3], 16)), chr(int(bytes[4], 16)))
            # 3 bytes of zero to provide stuffing for Wireshark
            msg += '%s%s%s' % (chr(int('00', 16)), chr(int('00', 16)), chr(int('00', 16)))
            # 8 data bytes
            msg += '%s%s%s%s%s%s%s%s' % (chr(int(bytes[5], 16)), chr(int(bytes[6], 16)), chr(int(bytes[7], 16)), chr(int(bytes[8], 16)), chr(int(bytes[9], 16)), chr(int(bytes[10], 16)), chr(int(bytes[11], 16)), chr(int(bytes[12], 16)))

            # write message
            f.write(msg)

        # close file
        f.close()

    
    # This method converts the data to integers and then passes it into parseMessageInt.
    # see that method for more documentation.
    def parseMessage(self,data):
        numData =[]
        for element in data:
            numData.append(ord(element))
        
        return self.parseMessageInt(numData)
    
    # This method will parse the CAN message input into the various components as integers.
    # The method will return the parsed information stored in a dictionary. Basic packet formation
    # error checking will be performed. Certain bits are always expected to be 0 as well as 
    # DLC must be 8 or less
    #
    # INPUT: CAN message as an array of integers corresponding to the hex read in
    #
    # OUTPUT: Dictionary containing the parsed information as follows
    # packet
    #    key:value
    #    msg: original full CAN message as a string
    #    sID: standard ID as integer
    #    ide: extended id identifier (1 means extended id)
    #    eID: extended ID as integer
    #    rb0: rb0 bit
    #    rb1: rb1 bit
    #    rtr: rtr bit
    #    length: DLC of packet
    #    db0: first data packet byte as integer
    #    db1: 2nd data packet byte as integer
    #     ...
    #    db8: nth data packet byte as integer
    #   
    #    NOTE: db1-8 are only assigned if the data byte contains info (see length int)
    def parseMessageInt(self,data):
        dp1 = data[0]
        dp2 = data[1]
        dp5 = data[4]
        
        #converts the CAN message to a string
        msg="";
        for bar in data:
            msg=msg+("%02x"%bar)
        
        packet = {'msg':msg}
        
        #get the ide bit. allows us to check to see if we have an extended
        #frame
        packet['ide'] = (dp2 & 0x0f)>>3
        #we have an extended frame
        if( packet['ide'] != 0):
            #get lower nibble, last 2 bits
            eId = dp2 & 0x03
            eId = eId<<8 | data[2]
            packet['eID'] = eId<<8 | data[3]
            packet['rtr'] = dp5>>6 & 0x01
    
        else:
            packet['rtr'] = dp2>>4 & 0x01
        
        #error check, 2nd msb of the lower nibble of byte 2 should be 0
        if( (dp2 & 0x04) == 4 ):
            packet['error'] = 1
        #error check an always 0 bit
        if( (dp5 & 0xf0) == 240):
            packet['error'] = 1
        
        # Create the standard ID. from the message
        packet['sID'] = dp1<<3 | dp2>>5
        
 
        length = dp5 & 0x0f
        packet['length'] = length
        
        if( length > 8):
            packet['error'] = 1
        
        #generate the data section
        for i in range(0,length):
            idx = 5+i
            dbidx = 'db%d' % i
            packet[dbidx] = data[idx]   
        return packet
    
    #this converts the packet to string with no spaces
    def packet2str(self,packet):
        toprint="";
        for bar in packet:
            toprint=toprint+("%02x"%ord(bar))
        return toprint;
    
    
    # This method will take a csv file as the file name and upload it to the MySQL 
    # database in the object. 
    def uploadData(self,filename):
        
        db_conn = MySQLdb.connect(self.host, self.username, self.password, self.db)
        cursor = db_conn.cursor()
        
        #load the data from the csv file
        try:
            
            fileObj = open(filename,'rU')
            data = self.opencsv(fileObj)
        except:
            print "Unable to open file!"
            return
        
        print "uploading data to SQL table, %s" % (self.table)
        #upload the data to the SQL database
        for packet in data:
            time = packet[0]
            error = packet[1]
            #could be None
            comment = packet[2]
            #get duration
            duration = packet[3]
            #get filterbit
            filter = packet[4]
            # parse the message
            parsedP = self.parseMessageInt(packet[5:])
            # generate the command
            cmd = self.getCmd(parsedP, time, error,duration,filter,comment)
            try:
                #execute the SQL command
                cursor.execute(cmd)
                #commit the changes to the database
                db_conn.commit()
            except:
                # Rollback in case  there is any error
                db_conn.rollback()
                
                #unable to add, raise an exception
                raise Exception, "Error inserting into db, %s with the command %s" % (self.db, cmd)
        print "data uplaod successful!"
        db_conn.close()
        
        
    # this file will open the csv file and parse out the information according to our standard
    # The returned value is a list of lists. Each row is a packet received and the columns are as defined
    # by our standard
    def opencsv(self,fileObj):
        reader = csv.reader(fileObj)
        rownum = 0
        data = []
        # for every row
        for row in reader:
            packet = []
            #check to see if the line begins with #
            # if it does it is a comment and should be ignored
            if( row[0][0] == '#'):
                rownum += 1
                continue
            colnum = 0;
            #go down each byte, the first one is the time
            for col in row:
                #time stamp
                if(colnum == 0):
                    packet.append(float(col))
                #error flag
                elif(colnum == 1):
                    packet.append(int(col))
                elif(colnum ==2):
                    packet.append(col)
                elif(colnum == 3):
                    packet.append(int(col))
                #data packets
                else:
                    packet.append(int(col,16))
                colnum += 1
                #print packet
            data.append(packet)
            rownum += 1
        #print data
        fileObj.close()
        return data

    # This will be used to read a file for writing packets on to the bus
    # The format below will assume a standard id but there will be easy extensible to make generic.
    # The format of the data in this case is assumed to be in hex
    # row format: will ignore any rows that begin with #
    # col 0: delay time from previous row (if empty no delay)
    # col 1: sID
    # COULD ADD eID column here
    # col2: DLC
    # col3: db0
    #  ...
    # colDLC
    def readWriteFileHex(self, filename):
        try:
            fileObj = open(filename,'rU')
        except:
            print "Unable to open file!"
            return
        
        reader = csv.reader(fileObj)
        rownum = 0
        data = []
        # for every row
        for row in reader:
            packet = []
            #check to see if the line begins with #
            # if it does it is a comment and should be ignored
            if( row[0][0] == '#'):
                rownum += 1
                continue
            colnum = 0;
            #go down each byte, the first one is the time
            for col in row:
                #time stamp
                if(colnum == 0):
                    packet.append(float(col))
                else:
                    packet.append(int(col,16))
                colnum += 1
                #print packet
            data.append(packet)
            rownum += 1
        #print data
        fileObj.close()
        return data
    
    # same as the readWriteFileHex but format is assumed to be in Decimal format
    def readWriteFileDEC(self,filename):
        try:
            fileObj = open(filename,'rU')
        except:
            print "Unable to open file!"
            return
        
        reader = csv.reader(fileObj)
        rownum = 0
        data = []
        # for every row
        for row in reader:
            packet = []
            #check to see if the line begins with #
            # if it does it is a comment and should be ignored
            if( row[0][0] == '#'):
                rownum += 1
                continue
            colnum = 0;
            #go down each byte, the first one is the time
            for col in row:
                #time stamp
                if(colnum == 0):
                    packet.append(float(col))
                else:
                    packet.append(int(col))
                colnum += 1
                #print packet
            data.append(packet)
            rownum += 1
        #print data
        fileObj.close()
        return data
    
    # will upload all the csv files in the self.DATALOCATION to the MySQL database
    # the files uploaded will be moved to a folder named as today's date and a tag _Uploaded will
    # be appended to the end of the filename
    def uploadFiles(self):
        #get all files in the ThayerData folder
        files = glob.glob(self.DATALOCATION+"*.csv")
        if( len(files) == 0):
            print "No new files to upload"
            return
        print files
        for file in files:
            #upload the file to the db
            self.uploadData(filename=file)
            
            #see if there is a folder with today's date
            now = datetime.datetime.now()
            datestr = now.strftime("%Y%m%d")
            path = self.DATALOCATION + datestr
            if( not os.path.exists(path)):
                #folder does not exists, create it
                os.mkdir(self.DATALOCATION+datestr)
            baseName = os.path.basename(file)
            root = file[:-len(baseName)]
            filename = root+datestr+"/"+baseName[:-4]+"_Uploaded.csv"
            print root
            print filename
            i=1
            #make sure the name is unique
            while( os.path.exists(filename)):
                filename = root+datestr+"/"+baseName[:-4]+"_Uploaded_%d.csv" %i
                i+=1 
            #change the name so to register that it has been uploaded
            print "file ",file
            print "filename ", filename
            os.rename(file, filename)        
        
# executes everything to run, inputs of the command lines
if __name__ == "__main__":
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,description='''\
    
        Data Management Program. The following options are available:
        
        upload csv file to MYSQL table
        write csv file to .pcap format
        ''')
        
    parser.add_argument('verb', choices=['upload','pcap','getDataPcap', 'getDataCSV', 'autoUpload', 'test'])
    parser.add_argument('-f','--filename1', help="Filename to upload from")
    parser.add_argument('-s','--filename2', help='Filename to save to')
    parser.add_argument('-t','--table', help="table to upload to SQL")
    parser.add_argument('--sql',help="SQL command to execute")
    
    
    args = parser.parse_args();
    verb = args.verb;
   
    # upload data to SQL server from csv file provided
    if( verb == "test"):
        dm = DataManage(host="thayerschool.org", db="thayersc_canbus",username="thayersc_canbus",password="c3E4&$39",table="ford_2004")
        dm.testSQLPCAP()
        
    if( verb == "upload"):
        filename = args.filename1
        table = args.table
        if( filename == None or table  == None):
            print " Error: must supply filename(-f) and table to upload to(-t)!"
            exit()
        dm = DataManage(host="thayerschool.org", db="thayersc_canbus",username="thayersc_canbus",password="c3E4&$39",table=table)
        dm.uploadData(filename)
        
    # This will automatically upload all the csv files in the ../ThayerData/ folder. The uploaded files will be moved inot a
    # different folder so that they will not be uploaded more than once.
    if( verb == "autoUpload"):
        if( filename == None or table  == None):
            print " Error: must supply filename(-f) and table to upload to(-t)!"
            exit()
        dm = DataManage(host="thayerschool.org", db="thayersc_canbus",username="thayersc_canbus",password="c3E4&$39",table=table)
        dm.uploadFiles()
    
    # create a .pcap file from the csv file provided
    if( verb == "pcap"):
        filename1 = args.filename1
        filename2 = args.filename2
        table = "placeHolder"
        dm = DataManage(host="thayerschool.org", db="thayersc_canbus",username="thayersc_canbus",password="c3E4&$39",table=table)
        dm.writePcapUpload(filenameUp=filename1, filenameWriteTo=filename2)
    
    #input sql command and get data. saved as a pcap file
    if( verb == "getDataPcap"):
        sql = args.sql
        filename2 = args.filename2
        if( sql == None or filename2 == None):
            print "ERROR: Must enter SQL command as well as filename to save to"
            exit()
        dm = DataManage(host="thayerschool.org", db="thayersc_canbus",username="thayersc_canbus",password="c3E4&$39",table=None)
        data = dm.getData(sql)
        print data
        dm.writeToPcap(filenameWriteTo=filename2, data=data)
    
    #input SQl command and get data.
    if( verb == "getDataCSV" ):
        sql = args.sql
        filename2 = args.filename2
        if( sql == None or filename2 == None):
            print "ERROR: Must enter SQL command as well as filename to save to"
            exit()
        dm = DataManage(host="thayerschool.org", db="thayersc_canbus",username="thayersc_canbus",password="c3E4&$39",table=None)
        data = dm.getData(sql)
        dm.writeDataCsv(data=data, filename=filename2)
        
