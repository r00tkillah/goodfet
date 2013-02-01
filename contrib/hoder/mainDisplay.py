
# Chris Hoder
# 11/3/2012

import Tkinter
import csv
import time
import sys;
import binascii;
import array;
from DataManage import DataManage
from experiments import *
import datetime
import os
import thread

sys.path.insert(0,'../../trunk/client/')
from GoodFETMCPCANCommunication import *
from GoodFETMCPCAN import GoodFETMCPCAN;
from intelhex import IntelHex;



# create a shorthand object for Tkinter so we don't have to type it all the time
tk = Tkinter

# This is a simple display class for the GOODTHOPTER10 board. It currently allows you to
# set the rate, sniff, write and save what is sniffed in 3 different forms. Raw, parsed, pcap.
# one can also store a time stamp on when a stimulus is added. All data will be written into the 
# following path ../../contrib/hoder/data/
class DisplayApp:

    # init function
    def __init__(self, width, height, rate=500, table="ford_2004"):
        
        self.SQL_NAME = "thayersc_canbus"
        self.SQL_HOST = "thayerschool.org"
        self.SQL_USERNAME = "thayersc_canbus"
        self.SQL_PASSWORD = "c3E4&$39"
        self.SQL_DATABASE = "thayersc_canbus"
        self.SQL_TABLE = table
        
        #configure information
        #Initialize communication class
        try:
            self.comm = GoodFETMCPCANCommunication()
        except:
            print "Board not properly connected. please connect and reset"
            self.comm = None
        self.running = False
        self.freq = 500
        self.verbose = True
        
        # Initialize the data manager

        self.dm = DataManage(host=self.SQL_HOST, db=self.SQL_DATABASE,username=self.SQL_USERNAME,password=self.SQL_PASSWORD,table=self.SQL_TABLE)
        
        #store figure
        self.fig = None
        
        #stimulus is initial not being conducted
        self.isStimulus = False
        
        #save the filenames, initialized when sniffing begins
        self.filenames = []

        # create a tk object, which is the root window
        self.root = tk.Tk()
        self.root.bind_class("Text","<Command-a>", self.selectall)
        # width and height of the window
        self.initDx = width
        self.initDy = height

        # set up the geometry for the window
        self.root.geometry( "%dx%d+50+30" % (self.initDx, self.initDy) )
        
        # set the title of the window
        self.root.title("CAN Data Reader")

        # set the maximum size of the window for resizing
        self.root.maxsize( 1024, 768 )

        # bring the window to the front
        self.root.lift()
        
        
        # setup the menus
        self.buildMenus()

        # build the controls
        self.buildControls()
        
        self.setBindings()

        
        # build the objects on the Canvas
        self.buildCanvas()

    def buildMenus(self):
        
        # create a new menu
        self.menu = tk.Menu(self.root)

        # set the root menu to our new menu
        self.root.config(menu = self.menu)

        # create a variable to hold the individual menus
        self.menulist = []

        # create a file menu
        filemenu = tk.Menu( self.menu )
        self.menu.add_cascade( label = "File", menu = filemenu )
        self.menulist.append(filemenu)

        # create another menu for kicks
        cmdmenu = tk.Menu( self.menu )
        self.menu.add_cascade( label = "Command", menu = cmdmenu )
        self.menulist.append(cmdmenu)

        # menu text for the elements
        menutext = [ [ 'Quit  \xE2\x8C\x98-Q', 'Settings ^, ' ],
                     [ '-', '-', '-' ] ]

        # menu callback functions
        menucmd = [ [ self.handleQuit, self.handleSettings],
                    [self.handleCmd1, self.handleCmd2, self.handleCmd3] ]
        
        # build the menu elements and callbacks
        for i in range( len( self.menulist ) ):
            for j in range( len( menutext[i]) ):
                if menutext[i][j] != '-':
                    self.menulist[i].add_command( label = menutext[i][j], command=menucmd[i][j] )
                else:
                    self.menulist[i].add_separator()
    
    
    def selectall(self, event):
        event.widget.tag_add("sel","1.0","end")

    # create the canvas object
    def buildCanvas(self):
        # this makes the canvas the same size as the window, but it could be smaller
        self.canvas = tk.Canvas( self.root, width=self.initDx, height=self.initDy)
        i = 0
    
        
        
        #filters
        entryLabel = Tkinter.Label(self.canvas,  font = "Helvetica 16 bold italic")
        entryLabel["text"] = "Filters:"
        entryLabel.grid(row=i,column=0, sticky=tk.W)
        entryLabel = Tkinter.Label(self.canvas)
        entryLabel["text"] = "Buffer 0:"
        entryLabel.grid(row=i,column =1, sticky=tk.E )
        entryLabel = Tkinter.Label(self.canvas)
        entryLabel["text"] = "Buffer 1:"
        entryLabel.grid(row=i,column =2 ,sticky=tk.W)
        i += 1
        self.filterIDs = []
        for k in range(0,2):
            for j in range(0,3):
                stdID = Tkinter.StringVar()
                stdID.set("")
                entryWidget = Tkinter.Entry(self.canvas, textvariable=stdID)
                self.filterIDs.append(stdID)
                entryWidget["width"] = 5
                entryWidget.grid(row=i+k,column=j+1, sticky=tk.E)
            print k
            i += 1
        clearButton = tk.Button( self.canvas, text="Clear", command=self.clearFilters, width=5)
        clearButton.grid(row=i,column=j+2,sticky=tk.W)
        i += 1
        
        #sniff button
        entryLabel = Tkinter.Label(self.canvas, font = "Helvetica 16 bold italic")
        entryLabel["text"] = "Sniff: "
        entryLabel.grid(row=i, column=0, sticky = tk.W)
        sniffButton = tk.Button( self.canvas, text="Start", command=self.sniff, width=5 )
        sniffButton.grid(row=i,column=1, sticky= tk.W)
        i += 1
        
        #time to sniff for
        entryLabel = Tkinter.Label(self.canvas)
        entryLabel["text"] = "Time (s):"
        entryLabel.grid(row=i,column=1, sticky=tk.E)
        self.time = Tkinter.StringVar();
        self.time.set("10")
        entryWidget = Tkinter.Entry(self.canvas, textvariable=self.time)
        entryWidget.grid(row=i,column=2, sticky=tk.E)
        entryWidget["width"] = 5
        i += 1
        
        #comment
        entryLabel = Tkinter.Label(self.canvas)
        entryLabel["text"] = "comment (sql):"
        entryLabel.grid(row=i,column=1, sticky = tk.E)
        self.comment = Tkinter.StringVar();
        self.comment.set("")
        entryWidget = Tkinter.Entry(self.canvas, textvariable=self.comment)
        entryWidget.grid(row=i,column=2, columnspan = 5)
        entryWidget["width"] = 30
        i += 1
        
        #description
        entryLabel = Tkinter.Label(self.canvas)
        entryLabel["text"] = "description (csv):"
        entryLabel.grid(row=i,column=1, sticky= tk.E)
        self.description = Tkinter.StringVar();
        self.description.set("")
        entryWidget = Tkinter.Entry(self.canvas, textvariable=self.description)
        entryWidget.grid(row=i,column=2, columnspan = 5)
        entryWidget["width"] = 30
        i += 1
        
#        self.fileBool = IntVar()
#        self.fileBool.set(0)
#        c = Checkbutton(self.canvas, variable = self.fileBool, command = self.fileCallback)
#        c.grid(row=i, column = 0)
#        i += 1
#        
        #writing
        entryLabel = Tkinter.Label(self.canvas,  font = "Helvetica 16 bold italic")
        entryLabel["text"] = "Write:"
        entryLabel.grid(row=i,column=0, sticky = tk.W)
        
        writeButton = tk.Button( self.canvas, text="Start", command=self.write, width=5 )
        writeButton.grid(row=i,column=1, sticky= tk.W)
        
        self.writeData = {}
        
        self.rtr = IntVar()
        self.rtr.set(0)
        c = Checkbutton(self.canvas,variable=self.rtr, text="rtr")
        c.grid(row=i,column=4, sticky = tk.W)
        
        entryLabel = Tkinter.Label(self.canvas, text="Time: ")
        entryLabel.grid(row=i,column=5,sticky=tk.W)
        
        varTemp = Tkinter.StringVar()
        self.writeData["Time"] = varTemp
        varTemp.set(10)
        entryWidget = Tkinter.Entry(self.canvas, width=5, textvariable=varTemp)
        entryWidget.grid(row=i, column=6, sticky=tk.W)
        i += 1
        
        
        entryLabel = Tkinter.Label(self.canvas)
        entryLabel["text"] = "sID:"
        entryLabel.grid(row=i,column=1, sticky= tk.E)
        varTemp = Tkinter.StringVar()
        self.writeData['sID'] = varTemp
        varTemp.set("")
        entryWidget = Tkinter.Entry(self.canvas, textvariable=varTemp)
        entryWidget.grid(row=i,column=2, sticky=tk.W)
        entryWidget["width"] = 5
        i += 1
        
        k = 0
        for j in range (0, 8, 2):
            entryLabel = Tkinter.Label(self.canvas)
            entryLabel["text"] = "db%d:" %k
            entryLabel.grid(row=i,column=j+1, sticky= tk.E)
            varTemp = Tkinter.StringVar()
            self.writeData['db%d'%(k)] = varTemp
            varTemp.set("")
            entryWidget = Tkinter.Entry(self.canvas, textvariable=varTemp)
            entryWidget.grid(row=i,column=j+2, sticky=tk.W)
            entryWidget["width"] = 5
            k += 1
            print k
            
        for j in range(0,8,2):
            entryLabel = Tkinter.Label(self.canvas)
            entryLabel["text"] = "db%d:" %((k))
            entryLabel.grid(row=i+1,column=j+1, sticky= tk.E)
            varTemp = Tkinter.StringVar()
            self.writeData['db%d'%((k))] = varTemp
            varTemp.set("")
            entryWidget = Tkinter.Entry(self.canvas, textvariable=varTemp)
            entryWidget.grid(row=i+1,column=j+2, sticky=tk.W)
            entryWidget["width"] = 5
            k +=1
    
        i += 2
       
        #sql
        entryLabel = Tkinter.Label(self.canvas,  font = "Helvetica 16 bold italic")
        entryLabel["text"] = "MYSQL:"
        entryLabel.grid(row=i,column=0, sticky = tk.W)
        sqlButton = tk.Button( self.canvas, text="Query", command=self.sqlQuery, width=5)
        sqlButton.grid(row=i,column=1,sticky=tk.W)
        
        self.pcapBool = IntVar()
        self.pcapBool.set(0)
        c = Checkbutton(self.canvas, variable = self.pcapBool, text="pcap")
        c.grid(row=i,column=2, sticky = tk.W)
                        
        self.csvBool = IntVar()
        self.csvBool.set(1)
        c = Checkbutton(self.canvas,variable=self.csvBool, text="csv")
        c.grid(row=i,column=3, sticky = tk.W)
        
        i += 1
        
        #text query box
        self.text = Tkinter.Text(self.canvas,borderwidth=10,insertborderwidth=10,padx=5,pady=2, width=50,height=5, highlightbackground="black")
        self.text.grid(row=i,column=0, columnspan=10,rowspan=2)
        i += 9
        
        
        #relative filename input
        entryLabel = Tkinter.Label(self.canvas)
        entryLabel["text"] = "Filename:"
        entryLabel.grid(row=i, column = 0,columnspan=2,stick=tk.E)
        self.queryFilename = Tkinter.StringVar()
        self.queryFilename.set("1.csv")
        entryWidget = Tkinter.Entry(self.canvas, textvariable=self.queryFilename)
        entryWidget.grid(row=i,column=2,columnspan=4)
        
        
        i += 1
        
        #expand it to the size of the window and fill
        self.canvas.pack( expand=tk.YES, fill=tk.BOTH)
        return


    # build a frame and put controls in it
    def buildControls(self):

        # make a control frame
        self.cntlframe = tk.Frame(self.root)
        self.cntlframe.pack(side=tk.TOP, padx=2, pady=2, fill=X)

        # make a separator line
        sep = tk.Frame( self.root, height=2, width=self.initDx, bd=1, relief=tk.SUNKEN )
        sep.pack( side=tk.TOP, padx = 2, pady = 2, fill=tk.Y)

        # make a cmd 1 button in the frame
        self.buttons = []
        #width should be in characters. stored in a touple with the first one being a tag
        self.buttons.append( ( 'cmd1', tk.Button( self.cntlframe, text="Experiments", command=self.experiments, width=10 ) ) )
        self.buttons[-1][1].pack(side=tk.LEFT)
        self.buttons.append( ( 'cmd1', tk.Button( self.cntlframe, text="Upload to db", command=self.uploaddb, width=10 ) ) )
        self.buttons[-1][1].pack(side=tk.LEFT)  # default side is top
        
        
        return

    #Bind callbacks with the keyboard/keys
    def setBindings(self):
        #self.root.bind( '<Button-1>', self.handleButton1 )
        #self.root.bind( '<Button-2>', self.handleButton2 )
        #self.root.bind( '<Button-3>', self.handleButton3 )
        #self.root.bind( '<B1-Motion>', self.handleButton1Motion )
        self.root.bind( '<Command-q>', self.handleModQ )
        self.root.bind( '<Control-s>', self.handleSettings)
        #self.root.bind( '<Command-o>', self.handleModO )
        self.root.bind( '<Control-q>', self.handleQuit )
        #self.root.bind('<Return>',self.handleStim )
        #self.root.bind('<Key>',self.handleKeys)

    # this method handles inputs when the user presses a key
    def handleKeys(self,event):
        print event.char
    
    #quits the GUI
    def handleQuit(self, event=None):
        print 'Terminating'
        self.root.destroy()
             
    def setDataManage(self,table, name, host, username, password, database):
        print "Resetting MYSQL database information"
        self.SQL_NAME = name
        self.SQL_HOST = host
        self.SQL_USERNAME = username
        self.SQL_PASSWORD = password
        self.SQL_DATABASE = database
        self.SQL_TABLE = table
        self.dm = DataManage(host=self.SQL_HOST, db=self.SQL_DATABASE,username=self.SQL_USERNAME,password=self.SQL_PASSWORD,table=self.SQL_TABLE)


    def handleSettings(self, event=None):
        data = {}
        dialogBox =  settingsDialog(parent = self.root, dClass = self, data=data, title = "Settings")
        
    #quits
    def handleModQ(self, event):
        self.handleQuit()

    # writes a row of data to the end of a csv file that is given by filename
    def writeRow(self,data,filename):
        writeFile  = open(filename,'a')
        dataWriter = csv.writer(writeFile,delimiter=',')
        dataWriter.writerow(data)
        writeFile.close()
        return
   
    def fileCallback(self):
        if( self.fileBool == 0):
            pass

    def setRunning(self):
        self.running = True
    
    def unsetRunning(self):
        self.running = False

    def getRate(self):
        return self.freq

    def connectBus(self):
        if( self.running):
            return
        try:
            self.comm = GoodFETMCPCANCommunication()
        except:
            print "Board not properly connected. please plug in the GoodThopter10 and re-attempt"
            self.comm = None

    #This method will check to see if we can do anything on the bus (i.e. if the chip is connected or being used)
    def checkComm(self):
        if(not self.isConnected() ):
            print "GoodThopter10 not connected. Please connect board"
            return False
        
        elif( self.running ):
            return False
        
        return True
    
    #set the rate on the MC2515
    def setRate(self,freq):
        if( not self.checkComm()):
            return
        self.comm.setRate(freq)
        
        
    # This method will clear all the filter inputs for the user
    def clearFilters(self):
        for element in self.filterIDs:
            element.set("")
    
    
    def sniff(self):
        if( not self.checkComm() ):
            return
        # get time and check that it is correct
        try:
            time = int(self.time.get())
        except:
            print "time in seconds as an integer"
        comments = self.comment.get()
        description = self.description.get()
        standardid = []
        # Get the filter ids and check to see if they are correctly an integer
        for element in self.filterIDs:
            if(element.get()==""):
                continue
            try:
                standardid.append(int(element.get()))
            except:
                print "Incorrectly formatted filters!"
                return
        if( len(standardid) == 0):
            standardid = None
        
        #sniff
        #self.comm.sniff(freq=self.freq,duration=time,
        #          description=description,verbose=self.verbose,comment=comments,filename = None,
        #           standardid=standardid, debug = False)    
        self.running = True
        thread.start_new_thread(self.comm.sniff, (self.freq, time, description, True, comments, None, standardid, False, False, True ))
        self.running = False
        
    def write(self):
        if( not self.checkComm()):
            return
        packet = []
        try:
            sID = int(self.writeData["sID"].get())
            #print "sid"
            timeStr = self.writeData["Time"].get()
            if( timeStr == ""):
                time = None
                repeat = False
            else:
                time = int(timeStr)
                repeat = True
            #print "attempts"
            #print self.writeData
            if( self.rtr.get() == 1):
                packet = None
            else:
                for j in range(0,8):
                    #print "db%d"%j
                    var = self.writeData.get("db%d"%j)
                    packet.append(int(var.get()))
        except:
            print "Invalid input!"
            return
        
            
        
        self.comm.spitSetup(self.freq)
        #for i in range(0,attempts):
        self.comm.spit(self.freq,[sID],repeat, duration=time, debug=False, packet=packet)
            
            
        #print "write Packet?"
        
    def uploaddb(self):
        print "Uploading all files"
        self.dm.uploadFiles()
        
    def experiments(self):
        data = {}
        exp = experiments(self.root, self, comm=self.comm, data = data, title = "Experiments")
        
        
        
    def sqlQuery(self):
        cmd = self.text.get(1.0,END)
        #check to see if there was any input
        if (cmd == chr(10)):
            print "No query input!"
            return
        data = self.dm.getData(cmd)
        filename = self.queryFilename.get()
        #make sure there is a directory for the file
        DATALOCATION = self.dm.getSQLLocation()
        now = datetime.datetime.now()
        datestr = now.strftime("%Y%m%d")
        path = DATALOCATION + datestr
        if(not os.path.exists(path)): 
            #folder does not exists, create it
            os.mkdir(DATALOCATION+datestr)
        #create full path relative to this folder
        filename = path + "/" + filename
        if( os.path.exists(filename)):
            filename2 = filename[:-4]+"_1"+filename[-4:]
            i=2
            #find the first unused filename
            while( os.path.exists(filename2)):
                filename2=filename[:-4]+("_%d" %i)+filename[-4:]
                i+=1
            filename=filename2
            print "file already exists name changed to %s" % filename
        self.dm.writeDataCsv(data,filename)
    
    def isConnected(self):
        return self.comm != None

    def handleCmd1(self):
        print "handling cmd1"
        return
    def handleCmd2(self):
        print "handling cmd2"
        return
    def handleCmd3(self):
        print "handling cmd3"
        return
    
    #run the method
    def main(self):
        print 'Entering main loop'
        #lets everything just sit and listen
        self.root.mainloop()
        

class settingsDialog(Toplevel):
    
    #constructor method
    def __init__(self, parent, dClass, data, title = None):
        
        Toplevel.__init__(self, parent)
        self.transient(parent)
        #top = self.top = Toplevel(parent)
        if title:
            self.title(title)
        #set parent
        self.parent = parent
        #set Data
        self.data = data
        self.dClass = dClass
        
        body = Frame(self)
        self.initial_focus = self.body(body)
        body.pack(padx=5,pady=5)
        
        self.buttonbox()
        
        self.grab_set()
        
        if not self.initial_focus:
            self.initial_focus = self
            
            
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        
        #positions the window relative to the parent
        self.geometry("+%d+%d" % (parent.winfo_rootx()+50, parent.winfo_rooty()+50))
        
        self.initial_focus.focus_set()
        
        self.wait_window(self)
        
    # This sets up the body of the popup dialog with all of the buttons and information
    def body(self,master):
        i=0
        
        #connect
        connectButton = tk.Button(master,text="Connect to Board", command = self.dClass.connectBus,width=20)
        connectButton.grid(row=i,column=0, sticky=tk.W,columnspan=3)
        i += 1
        
        #allows the user to set the rate
        entryLabel = Tkinter.Label(master)
        entryLabel["text"] = "Set Rate:"
        entryLabel.grid(row=i,column=0)
        self.rateChoice = tk.StringVar()
        self.rateChoice.set("500");
        self.rateMenu = tk.OptionMenu(master,self.rateChoice,"83.3","100","125","250","500","1000")
        self.rateMenu.grid(row=i,column=1)
        rateButton = tk.Button(master,text="Set Rate",command=self.setRate,width=10)
        rateButton.grid(row=i,column=2)
        i += 1
        
        
        # SQL database information
        entryLabel = Tkinter.Label(master)
        entryLabel["text"] = "MYSQL Database information:"
        entryLabel.grid(row=i,column=0, columnspan=3, sticky=tk.W)
        i += 1
        
        self.sqlDB = []
        
        #table
        entryLabel = Tkinter.Label(master)
        entryLabel["text"] = "Table:"
        entryLabel.grid(row=i,column=1, sticky = tk.W)
        sqlDbTemp = Tkinter.StringVar();
        sqlDbTemp.set(self.dClass.SQL_TABLE)
        self.sqlDB.append(sqlDbTemp)
        entryWidget = Tkinter.Entry(master, textvariable=sqlDbTemp)
        entryWidget.grid(row=i,column=2, columnspan = 3, sticky=tk.W)
        entryWidget["width"] = 30
        i += 1
        
    
       
        #Name
        entryLabel = Tkinter.Label(master)
        entryLabel["text"] = "Name:"
        entryLabel.grid(row=i,column=1, sticky = tk.W)
        sqlDbTemp = Tkinter.StringVar();
        sqlDbTemp.set(self.dClass.SQL_NAME)
        self.sqlDB.append(sqlDbTemp)
        entryWidget = Tkinter.Entry(master, textvariable=sqlDbTemp)
        entryWidget.grid(row=i,column=2, columnspan = 3, sticky=tk.W)
        entryWidget["width"] = 30
        i += 1
        
        #host
        entryLabel = Tkinter.Label(master)
        entryLabel["text"] = "Host:"
        entryLabel.grid(row=i,column=1, sticky = tk.W)
        sqlDbTemp = Tkinter.StringVar();
        sqlDbTemp.set(self.dClass.SQL_HOST)
        self.sqlDB.append(sqlDbTemp)
        entryWidget = Tkinter.Entry(master, textvariable=sqlDbTemp)
        entryWidget.grid(row=i,column=2, columnspan = 3, sticky=tk.W)
        entryWidget["width"] = 30
        i += 1
        
        #username
        entryLabel = Tkinter.Label(master)
        entryLabel["text"] = "Username:"
        entryLabel.grid(row=i,column=1, sticky = tk.W)
        sqlDbTemp = Tkinter.StringVar();
        sqlDbTemp.set(self.dClass.SQL_USERNAME)
        self.sqlDB.append(sqlDbTemp)
        entryWidget = Tkinter.Entry(master, textvariable=sqlDbTemp)
        entryWidget.grid(row=i,column=2, columnspan = 3, sticky=tk.W)
        entryWidget["width"] = 30
        i += 1
        
        #password
        entryLabel = Tkinter.Label(master)
        entryLabel["text"] = "Password:"
        entryLabel.grid(row=i,column=1, sticky = tk.W)
        sqlDbTemp = Tkinter.StringVar();
        sqlDbTemp.set(self.dClass.SQL_PASSWORD)
        self.sqlDB.append(sqlDbTemp)
        entryWidget = Tkinter.Entry(master, textvariable=sqlDbTemp, show="*")
        entryWidget.grid(row=i,column=2, columnspan = 3, sticky=tk.W)
        entryWidget["width"] = 30
        i += 1
        
        #Database
        entryLabel = Tkinter.Label(master)
        entryLabel["text"] = "Database:"
        entryLabel.grid(row=i,column=1, sticky = tk.W)
        sqlDbTemp = Tkinter.StringVar();
        sqlDbTemp.set(self.dClass.SQL_DATABASE)
        self.sqlDB.append(sqlDbTemp)
        entryWidget = Tkinter.Entry(master, textvariable=sqlDbTemp)
        entryWidget.grid(row=i,column=2, columnspan = 3, sticky=tk.W)
        entryWidget["width"] = 30
        i += 1
        
    def setRate(self):
        rate = self.rateChoice.get()
        self.dClass.setRate(rate)
        
    
    #This is the cancel / ok button
    def buttonbox(self):
        #add standard button box
        box = Frame(self)
        
        #ok button
        w = Button(box, text="Apply", width = 10, command = self.ok, default=ACTIVE)
        w.pack(side=LEFT,padx=5,pady=5)
        # cancel button
        w = Button(box,text="Cancel", width=10,command = self.cancel)
        w.pack(side=LEFT,padx=5,pady=5)
        
        self.bind("<Return>",self.ok)
        self.bind("<Escape>",self.cancel)
        
        box.pack()
        
    # ok button will first validate the choices (see validate method) and then exit the dialog
    # if everything is ok 
    def ok(self, event = None):
        if not self.validate():
            self.initial_focus.focus_set() #put focus back
            return
        
        table = "%s"% self.sqlDB[0].get()
        print table
        name = self.sqlDB[1].get()
        host = self.sqlDB[2].get()
        username = self.sqlDB[3].get()
        password = self.sqlDB[4].get()
        database =self.sqlDB[5].get() 
        self.dClass.setDataManage(table = table, name = name, host = host, \
                                  username = username, password = password, database = database )
        
        self.withdraw()
        self.update_idletasks()
        self.apply()
        self.parent.focus_set()
        self.destroy()
        return 1
        
    # this is a cancel button which will just exit the dialog and should not plot anything
    def cancel(self, event = None):
        self.data.clear()
    
        #put focus back on parent window
        self.parent.focus_set()
        self.destroy()
        return 0
       
    #this tests to make sure that there are inputs 
    def validate(self):
        #returns 1 if everything is ok
        return 1
    
    #this method is called right before exiting. it will set the input dictionary with the information for
    # the display method to grab the data and graph it
    def apply(self):
        
            
        return
        
# executes everything to run
if __name__ == "__main__":
    dapp = DisplayApp(650, 520, "ford_2004")
    dapp.main()
