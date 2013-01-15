# Chris Hoder
# 1/11/2012

import MySQLdb
import sys
import csv

#data parsing assumes an extended ID!!

class DataManage:
    
    
    def __init__(self, host, db, username, password, table):
        
        # Save MYSQL information for later use
        self.host = host
        self.db = db
        self.username = username
        self.password = password
        self.table = table
       
       
    #Creates a new MySQL table in the database with the given table name
    # UNTESTED 
    def createTable(self, table):
        self.table = table
        cmd = "CREATE TABLE `%s` (\
              `id` int(11) unsigned NOT NULL AUTO_INCREMENT, \
              `time` float unsigned NOT NULL, \
              `stdID` int(5) unsigned NOT NULL, \
              `exID` int(5) unsigned DEFAULT NULL, \
              `length` int(1) unsigned NOT NULL, \
              `error` bit(1) NOT NULL, \
              `remote frame` bit(1) NOT NULL DEFAULT b'0', \
              `msg` varchar(30) NOT NULL DEFAULT '', \
              `db0` int(3) unsigned DEFAULT NULL, \
              `db1` int(3) unsigned DEFAULT NULL, \
              `db2` int(3) unsigned DEFAULT NULL, \
              `db3` int(3) unsigned DEFAULT NULL, \
              `db4` int(3) unsigned DEFAULT NULL, \
              `db5` int(3) unsigned DEFAULT NULL, \
              `db6` int(3) unsigned DEFAULT NULL, \
              `db7` int(3) unsigned DEFAULT NULL, \
              PRIMARY KEY (`id`)  \
              ) ENGINE=MyISAM DEFAULT CHARSET=utf8;" % (table)
        self.addData(cmd)
        
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
            raise Exception, "Error fetching data from db, %s with the command, %s" % self.db, cmd
        
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
    def getCmd(self,packet,time,error):
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
        cmd += ' error, remoteFrame, msg) VALUES (%f, %d' % (time, packet['sID'])
        
        #if there is an extended id include it
        if(packet.get('eID')):
            cmd += ", %d" % packet['eID']
        
        cmd += ", %d" % length
        
        #add data
        for i in range(0,length):
            cmd += ", %d" % (packet['db'+str(i)])
        
        cmd += ', %d, %d, "%s")' % (error, packet['rtr'], packet['msg'])
         
        return cmd
    
    def writeDataCsv(self,data, filename):
        pass
    
    def writePcap(self,data,filename):
        pass

    
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
        
        #upload the data to the SQL database
        for packet in data:
            time = packet[0]
            error = packet[1]
            # parse the message
            print "packet \n", packet
            parsedP = self.parseMessageInt(packet[2:])
            # generate the command
            cmd = self.getCmd(parsedP, time, error)
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
            print row
            packet = []
            #this is the header row, we can ignore
            if rownum == 0:
                rownum += 1
                continue
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
                #data packets
                else:
                    packet.append(int(col,16))
                colnum += 1
                #print packet
            data.append(packet)
            rownum += 1
        #print data
        return data

# executes everything to run, inputs of the command lines
if __name__ == "__main__":
    if( len(sys.argv) != 3):
        print len(sys.argv)
        print sys.argv
        print "Error. Invalid Arguments! \n \
This will upload the given csv file \n \
to the SQL database table chosen \n \
USAGE: >> python DataManage.py [SQLtable] [filename] \n" 
                      
        exit()
    
    table = sys.argv[1]
    filename = sys.argv[2]
    dataM = DataManage(host="thayerschool.org", db="thayersc_canbus",username="thayersc_canbus",password="c3E4&$39",table=table)
    dataM.uploadData(filename)