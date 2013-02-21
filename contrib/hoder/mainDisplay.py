
# Chris Hoder
# 11/3/2012

import Tkinter
import csv
import time
import sys;
import binascii;
import array;
from DataManage import DataManage
from tkFileDialog import askopenfilename
import tkMessageBox
from experimentsGUI import *
from info import *
import tkHyperlinkManager
import datetime
import os
import thread
import ConfigParser

sys.path.insert(0,'../../trunk/client/')
from GoodFETMCPCANCommunication import *
from GoodFETMCPCAN import GoodFETMCPCAN;
from experiments import experiments
from intelhex import IntelHex;



# create a shorthand object for Tkinter so we don't have to type it all the time
tk = Tkinter 
""" Shortcut for Tkinter """


class DisplayApp:
    """ 
    This is the main display for the graphical user interface (GUI). This GUI is designed to aid 
    the user in their work listening to CAN traffic via the GOODTHOPTER10 board, U{http://goodfet.sourceforge.net/hardware/goodthopter10/}.
    There are no inputs to this class but all default data is loaded from the settings file.
    
    """   

    # init function
    def __init__(self):
        self.BOLDFONT = "Helvetica 16 bold italic"
        self.SETTINGS_FILE = "./Settings.ini"
        """ This stores the location of the file where settings are saved"""
        Config = ConfigParser.ConfigParser()
        try:
            fileObj = open(self.SETTINGS_FILE)
            results = Config.read(self.SETTINGS_FILE)
        except Error, msg:
            print "Error Parsing Config File."
            print msg
        else:
            if( results == []):
                print "Could not load config file %s"%self.SETTINGS_FILE
        
        # Initialize the data manager
        self.DATA_LOCATION = self.ConfigSectionMap(Config, "FileLocations")['data_location']
       
        dmData = self.ConfigSectionMap(Config,"DataManager")
        #print a
        #cfgfile = open(self.SETTINGS_FILE)
        
        
        self.SQL_NAME = dmData['sql_name'] 
        self.SQL_HOST = dmData['sql_host']
        self.SQL_USERNAME = dmData['sql_username']
        self.SQL_PASSWORD = dmData['sql_password']
        self.SQL_DATABASE = dmData['sql_database']
        self.SQL_TABLE = dmData['sql_table']
        self.dm = DataManage(host=self.SQL_HOST, db=self.SQL_DATABASE,username=self.SQL_USERNAME,password=self.SQL_PASSWORD,table=self.SQL_TABLE, dataLocation = self.DATA_LOCATION)
        
        windowInfo = self.ConfigSectionMap(Config, "WindowSize")
        # width and height of the window
        self.initDx = int(windowInfo['width'])
        self.initDy = int(windowInfo['height'])
        self.dataDx =80;
        #self.dataDx = (self.initDx/2-350);
       
        self.dataDy = self.initDy;
        #self.ControlsDx = (self.initDx - 80);
        self.ControlsDx = 400;
        self.ControlsDy = self.initDy;
        
        #configure information
        #Initialize communication class
        
        """ This is a boolean which when false tells you that there is a thread communicating with the bus at the moment"""
        self.freq = float(self.ConfigSectionMap(Config, "BusInfo")['frequency']) 
        """ Bus frequency """
        self.verbose = True 
        

        # create a tk object, which is the root window
        self.root = tk.Tk() 
        """ Stores the tk object for the window """ 
        self.root.bind_class("Text","<Command-a>", self.selectall) # rebinds the select all feature
        
        
        
        self.csvBool = Tkinter.IntVar() 
        """ 1 if sql query is to be stored as a csv document, 0 otherwise """
        self.sqlSaveCsvChoice = True 
        """ True if data is to be saved as a csv document """
        # set up the geometry for the window
        self.root.geometry( "%dx%d+50+30" % (self.initDx, self.initDy) )
        
        # set the title of the window
        self.root.title("CAN Data Reader")

        # set the maximum size of the window for resizing
        #self.root.maxsize( 1024, 768 )

        # bring the window to the front
        self.root.lift()
        
        
        # setup the menus
        self.buildMenus()

        # build the controls
        self.buildControls()
        
        self.setBindings()
        
        self.buildDataCanvas()
        
        self.RightSideCanvas = tk.Canvas( self.root, width=self.ControlsDx, height=self.ControlsDy)
        # build the objects on the Canvas
        self.blankCanvas = tk.Canvas(self.RightSideCanvas,width=self.ControlsDx*10,height=self.ControlsDy*10)
        self.blankCanvas.grid(row=0,column=0)
        
        self.buildCanvas()
        self.buildExperimentCanvas()
        self.buildSQLCanvas()
        self.buildInfoFrame()
        self.RightSideCanvas.pack(side=tk.RIGHT,expand=tk.YES,fill=tk.BOTH)
        #tk.Misc.lift(self.blankCanvas, aboveThis=self.sniffFrame)
        self.sniffFrameLift()
    
        self.running = Tkinter.IntVar()
        self.running.set(0)
        self.running.trace('w',self.updateStatus)
        
        try:
            #self.comm = GoodFETMCPCANCommunication()
            self.comm = experiments(self.DATA_LOCATION)
            self.statusLabel.config(bg="green")
            self.statusString.set("Ready")
            """ Stores the class which communicates with the bus """
        except:
            print "Board not properly connected. please connect and reset"
            self.comm = None
            self.statusLabel.config(bg="red")
            self.statusString.set("Not Connected")
        #self.running = False 
        
  
    def writeiniFile(self, filename, section, option, value):
        """ 
        Writes the given settings to the given settings filename. If the section does not exist in the settings file
        then it will be created. The file is assumed to be a .ini file. This method is a modified version of the
        one found on the following website: U{http://bytes.com/topic/python/answers/627791-writing-file-using-configparser}
        
        @type filename: string
        @param filename: path to the settings file
        @type section: string
        @param section: section heading in the settings file
        @param option: string
        @param option: The option in the given section in the settings file that will be set
        @param value: The value of the option we are saving. 
        """
        Config = None
        Config = ConfigParser.ConfigParser()
        Config.read(filename)
        if not Config.has_section( section ): #create the section
            Config.add_section(section)
        Config.set(section, option, value)
        Config.write(open(filename,'w'))
        
    #modified from the following example:
    # http://wiki.python.org/moin/ConfigParserExamples
    def ConfigSectionMap(self, Config, section):
        """
        This method has been implemented based on the following exmaple, U{http://wiki.python.org/moin/ConfigParserExamples}.
        
        @param Config: ConfigParser instance that has already read the given settings filename.
        @type section: string
        @param section: Section that you want to get all of the elements of from the settings file that has been
                        read by the Config parser and passed in as Config.
        @rtype: Dictionary
        @return: Dictionary where they keys are the options in the given section and the values are the corresponding
                 settings value.
        """
        dict1 = {}
        options = Config.options(section)
        for option in options:
            try:
                dict1[option] = Config.get(section,option)
                if( dict1[option] == 1):
                    print "Skipped loading option: %s" %option
            except:
                print "Cannot load settings file. Crash on %s"%option
                dict1[option] = None
        return dict1
         
    def buildMenus(self):
        """
        This method will build the menu bars
        """
        
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
        menutext = [ [ 'Quit  \xE2\x8C\x98-Q', 'Settings ^. ' ],
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
        """ 
        This method is called when the user wishes to select the entire text box.
        """
        event.widget.tag_add("sel","1.0","end")


    def buildExperimentCanvas(self):
        self.experimentFrame = Tkinter.Frame(self.RightSideCanvas, width=self.ControlsDx, height=self.ControlsDy)
        i=0
        #Sweep all ids experiments
        j = 0
        entryLabel = Tkinter.Label(self.experimentFrame, font = self.BOLDFONT)
        entryLabel["text"] = "Sweep Std IDs:"
        entryLabel.grid(row=i,column=j,columnspan=3, sticky = tk.W)
        
        i+=1
        j = 0
        entryLabel=Tkinter.Label(self.experimentFrame)
        entryLabel["text"] = "Time (s):"
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j+=1
        self.sniffTime = Tkinter.StringVar();
        self.sniffTime.set("2")
        entryWidget = Tkinter.Entry(self.experimentFrame, textvariable=self.sniffTime)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=j, sticky=tk.W)
        j+=1
        #align with lower exp
        j += 2
        entryLabel = Tkinter.Label(self.experimentFrame)
        entryLabel["text"] = "From: "
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j+=1
        self.lowSweep = Tkinter.StringVar();
        self.lowSweep.set("0")
        entryWidget = Tkinter.Entry(self.experimentFrame, textvariable=self.lowSweep)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        j+=1
        entryLabel = Tkinter.Label(self.experimentFrame)
        entryLabel["text"] = "To "
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j+=1
        self.HighSweep = Tkinter.StringVar();
        self.HighSweep.set("4095")
        entryWidget = Tkinter.Entry(self.experimentFrame, textvariable=self.HighSweep)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        j+= 1
        sweepButton = Button(self.experimentFrame, text="Start", width=5, command=self.sweepID)
        sweepButton.grid(row=i, column=j,sticky=tk.W)
        
        i += 1
        j = 0
        entryLabel = Tkinter.Label(self.experimentFrame, font = self.BOLDFONT)
        entryLabel["text"] = "RTR sweep response:"
        entryLabel.grid(row=i,column=j,columnspan=3, sticky = tk.W)
        
        i+=1
        j = 0 
        entryLabel=Tkinter.Label(self.experimentFrame)
        entryLabel["text"] = "Time (s):"
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j += 1
        #self.sniffTime = Tkinter.StringVar();
        #self.sniffTime.set("20")
        entryWidget = Tkinter.Entry(self.experimentFrame, textvariable=self.sniffTime)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=j, sticky=tk.W)
        j += 1
        entryLabel = Tkinter.Label(self.experimentFrame, text = "Attempts: ")
        entryLabel.grid(row=i, column = j, sticky=tk.W)
        j += 1
        self.attempts = Tkinter.StringVar();
        self.attempts.set("1")
        entryWidget = Tkinter.Entry(self.experimentFrame, textvariable = self.attempts)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        j += 1
        entryLabel = Tkinter.Label(self.experimentFrame)
        entryLabel["text"] = "From: "
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j += 1
        #self.lowSweep = Tkinter.StringVar();
        #self.lowSweep.set("0")
        entryWidget = Tkinter.Entry(self.experimentFrame, textvariable=self.lowSweep)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        j += 1
        entryLabel = Tkinter.Label(self.experimentFrame)
        entryLabel["text"] = "To "
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j += 1
        #self.HighSweep = Tkinter.StringVar();
        #self.HighSweep.set("4095")
        entryWidget = Tkinter.Entry(self.experimentFrame, textvariable=self.HighSweep)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        j += 1
        sweepButton = Button(self.experimentFrame, text="Start", width=5, command=self.RTRsweepID)
        sweepButton.grid(row=i, column=j,sticky=tk.W)
        j += 1
        i+= 1
        j = 0
        entryLabel = Tkinter.Label(self.experimentFrame,font=self.BOLDFONT)
        entryLabel["text"] = "Fuzz all possible packets"
        entryLabel.grid(row=i,column=j,columnspan=3,stick=tk.W)
        j+=3
        startButton = Tkinter.Button(self.experimentFrame,text="Start",width=5,command=self.generalFuzz)
        startButton.grid(row=i,column=j,sticky=tk.W)
        j+=1
        
        i+=1
        j=0
        self.generalFuzzData = {}
        entryLabel = Tkinter.Label(self.experimentFrame)
        entryLabel["text"] = "Period (ms): "
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j +=1
        period = Tkinter.StringVar()
        period.set("")
        self.generalFuzzData['period'] = period
        entryWidget = Tkinter.Entry(self.experimentFrame, textvariable=period)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        j += 1
        
        entryLabel = Tkinter.Label(self.experimentFrame)
        entryLabel["text"] = "Writes: "
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j +=1
        writesPerFuzz = Tkinter.StringVar()
        writesPerFuzz.set("")
        self.generalFuzzData['writesPerFuzz'] = writesPerFuzz
        entryWidget = Tkinter.Entry(self.experimentFrame, textvariable=writesPerFuzz)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=j,sticky=tk.W)
     
        j += 1
        entryLabel = Tkinter.Label(self.experimentFrame)
        entryLabel["text"] = "Fuzzes : "
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j +=1
        Fuzzes = Tkinter.StringVar()
        Fuzzes.set("")
        self.generalFuzzData['Fuzzes'] = Fuzzes
        entryWidget = Tkinter.Entry(self.experimentFrame, textvariable=Fuzzes)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        
        j = 0
        i += 1
        entryLabel = Tkinter.Label(self.experimentFrame, font = self.BOLDFONT)
        entryLabel["text"] = "Generation Fuzzing:"
        entryLabel.grid(row=i,column=j,columnspan=3, sticky = tk.W)
        j +=3
        startButton = Tkinter.Button(self.experimentFrame,text="Start",width=5,command=self.GenerationFuzz)
        startButton.grid(row=i,column=j,sticky=tk.W)
        i+=1
        self.fuzzData = {}
        j = 0 
        entryLabel = Tkinter.Label(self.experimentFrame)
        entryLabel["text"] = "sID: "
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j +=1
        sID = Tkinter.StringVar()
        sID.set("")
        self.fuzzData['sIDs'] = sID
        entryWidget = Tkinter.Entry(self.experimentFrame, textvariable=sID)
        entryWidget["width"] = 40
        entryWidget.grid(row=i,column=j,columnspan=8,sticky=tk.W)
        j += 1
        i += 1
        j = 0
        entryLabel = Tkinter.Label(self.experimentFrame)
        entryLabel["text"] = "Period (ms): "
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j +=1
        period = Tkinter.StringVar()
        period.set("")
        self.fuzzData['period'] = period
        entryWidget = Tkinter.Entry(self.experimentFrame, textvariable=period)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        j += 1
        
        entryLabel = Tkinter.Label(self.experimentFrame)
        entryLabel["text"] = "Writes: "
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j +=1
        writesPerFuzz = Tkinter.StringVar()
        writesPerFuzz.set("")
        self.fuzzData['writesPerFuzz'] = writesPerFuzz
        entryWidget = Tkinter.Entry(self.experimentFrame, textvariable=writesPerFuzz)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=j,sticky=tk.W)
     
        j += 1
        entryLabel = Tkinter.Label(self.experimentFrame)
        entryLabel["text"] = "Fuzzes : "
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j +=1
        Fuzzes = Tkinter.StringVar()
        Fuzzes.set("")
        self.fuzzData['Fuzzes'] = Fuzzes
        entryWidget = Tkinter.Entry(self.experimentFrame, textvariable=Fuzzes)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        
        i+=1 
        j = 0
        for k in range(1,11,3):
            entryLabel = Tkinter.Label(self.experimentFrame)
            entryLabel["text"] = "low"
            entryLabel.grid(row=i,column=k)
            entryLabel = Tkinter.Label(self.experimentFrame)
            entryLabel["text"] = "high"
            entryLabel.grid(row=i,column=k+1)
        i += 1
        j = 0
        k = 0
        for j in range (0, 12, 3):
            entryLabel = Tkinter.Label(self.experimentFrame)
            entryLabel["text"] = "db%d:" %k
            entryLabel.grid(row=i,column=j, sticky= tk.W)
            varTempLow = Tkinter.StringVar()
            #self.fuzzData['db%d'%(k)] = varTempLow
            varTempLow.set("")
            entryWidget = Tkinter.Entry(self.experimentFrame, textvariable=varTempLow)
            entryWidget.grid(row=i,column=j+1, sticky=tk.W)
            entryWidget["width"] = 5
            varTempHigh = Tkinter.StringVar()
            self.fuzzData['db%d'%(k)] = [varTempLow, varTempHigh]
            entryWidget = Tkinter.Entry(self.experimentFrame, textvariable = varTempHigh)
            entryWidget["width"] = 5
            entryWidget.grid(row=i,column=j+2,sticky=tk.W)
            k += 1
            print k
        
        for j in range(0,12,3):
            entryLabel = Tkinter.Label(self.experimentFrame)
            entryLabel["text"] = "db%d:" %((k))
            entryLabel.grid(row=i+1,column=j, sticky= tk.W)
            varTempLow = Tkinter.StringVar()
            #self.fuzzData['db%d'%((k))] = varTemp
            varTempLow.set("")
            entryWidget = Tkinter.Entry(self.experimentFrame, textvariable=varTempLow)
            entryWidget.grid(row=i+1,column=j+1, sticky=tk.W)
            entryWidget["width"] = 5
            varTempHigh = Tkinter.StringVar()
            self.fuzzData['db%d'%(k)] = [varTempLow, varTempHigh]
            entryWidget = Tkinter.Entry(self.experimentFrame, textvariable = varTempHigh)
            entryWidget["width"] = 5
            entryWidget.grid(row=i+1,column=j+2,sticky=tk.W)
            k +=1
    
        i += 2
        j=0
        entryLabel = Tkinter.Label(self.experimentFrame, font = self.BOLDFONT)
        entryLabel["text"] = "Re-inject Fuzzed Packets:"
        entryLabel.grid(row=i,column=j,columnspan=3, sticky = tk.W)
        j +=3
        startButton = Tkinter.Button(self.experimentFrame,text="Start",width=5,command=self.reInjectFuzzed)
        startButton.grid(row=i,column=j,sticky=tk.W)
        i+=1
        j = 0
        self.reInjectData = {}
        entryLabel = Tkinter.Label(self.experimentFrame,text="sID: ")
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j+= 1
        varID = Tkinter.StringVar()
        varID.set("")
        self.reInjectData['sID'] = varID
        entryWidget = Tkinter.Entry(self.experimentFrame, textvariable=varID,width=5)
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        j+=1
        # The injection files are all saved by date
        entryLabel = Tkinter.Label(self.experimentFrame,text="Date: ")
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j+= 1
        varID = Tkinter.StringVar()
        now = datetime.datetime.now()
        varID.set(now.strftime("%Y%m%d")) # automatically fill with today's date
        self.reInjectData['date'] = varID
        entryWidget = Tkinter.Entry(self.experimentFrame, textvariable=varID,width=10)
        entryWidget.grid(row=i,column=j,columnspan=2,sticky=tk.W)
        j+= 2
        # The injection files are all saved by date
        entryLabel = Tkinter.Label(self.experimentFrame,text="Start (HHMM): ")
        entryLabel.grid(row=i,column=j,columnspan=2,sticky=tk.W)
        j+= 2
        varID = Tkinter.StringVar()
       
        varID.set("") # automatically fill with today's date
        self.reInjectData['startTime'] = varID
        entryWidget = Tkinter.Entry(self.experimentFrame, textvariable=varID,width=5)
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        j+= 1
        # The injection files are all saved by date
        entryLabel = Tkinter.Label(self.experimentFrame,text="END (HHMM): ")
        entryLabel.grid(row=i,column=j,columnspan = 2, sticky=tk.W)
        j+= 2
        varID = Tkinter.StringVar()
       
        varID.set("") # automatically fill with today's date
        self.reInjectData['endTime'] = varID
        entryWidget = Tkinter.Entry(self.experimentFrame, textvariable=varID,width=5)
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        j+= 1
        
        i+= 1
        j = 0
        
        entryLabel = Tkinter.Label(self.experimentFrame, font = self.BOLDFONT)
        entryLabel["text"] = "Packet Response:"
        entryLabel.grid(row=i,column=j,columnspan=3, sticky = tk.W)
        j +=3
        startButton = Tkinter.Button(self.experimentFrame,text="Start",width=5,command=self.packetResponse)
        startButton.grid(row=i,column=j,sticky=tk.W)
        i+=1
        self.packetResponseData = {}
        j = 0 
        entryLabel = Tkinter.Label(self.experimentFrame,text="Time:")
        entryLabel.grid(row=i,column=j,sticky = tk.W)
        j += 1
        varID = Tkinter.StringVar()
        varID.set("30")
        self.packetResponseData['time'] = varID
        entryWidget = Tkinter.Entry(self.experimentFrame,textvariable=varID,width=5)
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        j += 1
        entryLabel = Tkinter.Label(self.experimentFrame,text="repeats:")
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j += 1
        varID = Tkinter.StringVar()
        varID.set("100")
        self.packetResponseData["repeats"] = varID
        entryWidget = Tkinter.Entry(self.experimentFrame,textvariable=varID,width=5)
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        j += 1
        entryLabel = Tkinter.Label(self.experimentFrame,text="period (ms):")
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j+=1
        varID = Tkinter.StringVar()
        varID.set("1")
        self.packetResponseData["period"] = varID
        entryWidget = Tkinter.Entry(self.experimentFrame,textvariable=varID,width=5)
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        i+=1
        j = 0
        entryLabel = Tkinter.Label(self.experimentFrame,text="listenID: ")
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j += 1
        varID = Tkinter.StringVar()
        varID.set("")
        self.packetResponseData['listenID'] = varID
        entryWidget = Tkinter.Entry(self.experimentFrame,textvariable=varID, width=5)
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        j +=1
        entryLabel = tk.Label(self.experimentFrame,text="data:")
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j += 1
        for k in range(0,8):
            varID = tk.StringVar()
            varID.set("")
            idx = 'Listen_db%d'%k
            self.packetResponseData[idx] = varID
            entryWidget = tk.Entry(self.experimentFrame,textvariable=varID,width=5)
            entryWidget.grid(row=i,column=j,sticky=tk.W)
            j += 1
        i += 1
        j = 0
        entryLabel = tk.Label(self.experimentFrame,text="Res.ID:")
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j+=1
        varID = tk.StringVar()
        varID.set("")
        self.packetResponseData["responseID"] = varID
        entryWidget = Tkinter.Entry(self.experimentFrame,textvariable=varID,width=5)
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        j+=1
        entryLabel = tk.Label(self.experimentFrame,text="data:")
        entryLabel.grid(row=i,column=j,stick=tk.W)
        j += 1
        for k in range(0,8):
            varID = tk.StringVar()
            varID.set("")
            idx = 'Response_db%d'%k
            self.packetResponseData[idx] = varID
            entryWidget = tk.Entry(self.experimentFrame,textvariable=varID,width=5)
            entryWidget.grid(row=i,column=j,sticky=tk.W)
            j+=1
        #pass
        
        self.experimentFrame.grid(row=0,column=0,sticky=tk.W+tk.N,pady=0)

    def buildInfoFrame(self):
        self.infoFrame = tk.Frame(self.RightSideCanvas, width=self.ControlsDx, height=self.ControlsDy)
        entryLabel = Tkinter.Label(self.infoFrame, text="ArbID: ")
        entryLabel.grid(row=0,column=0)
        self.options = ["INSERT","insert"]
        self.IDchoice = Tkinter.StringVar()
        self.IDchoice.set(self.options[0])
        self.IDchoice.trace('w',self.updateInfo)
        #self.splitChoice = OptionMenu(self.canvas, self.splitValue, *keys)
        idChoiceOptions= OptionMenu(self.infoFrame,self.IDchoice, *tuple(self.options))
        idChoiceOptions.grid(row=0,column=1)
        
        self.infoFrame.grid(row=0,column=0,sticky=tk.N+tk.W)
        
        
    
    def updateInfo(self, name, index, mode):
        print "name: ", name
        print "index: ", index
        print "mode: ", mode
        print "change"  
        
    def buildSQLCanvas(self):
        self.sqlFrame = tk.Frame(self.RightSideCanvas, width = self.ControlsDx, height=self.ControlsDy)
        i = 0;
        sqlButton = tk.Button(self.sqlFrame,text="Upload Sniffed Packets to Database", command=self.uploaddb, width=30)
        sqlButton.grid(row=i,column=0,columnspan=3,sticky=tk.W)
        i+=1;
        #self.buttons.append( ( 'cmd2', tk.Button( self.cntlframe, text="Upload to db", command=self.uploaddb, width=10 ) ) )
        #self.buttons[-1][1].pack(side=tk.LEFT)  # default side is top
        #sql
        entryLabel = Tkinter.Label(self.sqlFrame,  font = self.BOLDFONT)
        entryLabel["text"] = "MYSQL:"
        entryLabel.grid(row=i,column=0, sticky = tk.W)
        sqlButton = tk.Button( self.sqlFrame, text="Query", command=self.sqlQuery, width=4)
        sqlButton.grid(row=i,column=1,sticky=tk.W)
        
        self.pcapBool = IntVar()
        #self.pcapBool.trace('w', self.sqlSaveType)
        self.pcapBool.set(0)
        c = Checkbutton(self.sqlFrame, variable = self.pcapBool, text="pcap")
        c.grid(row=i,column=2, sticky = tk.W)
                        
        self.csvBool = IntVar()
        self.csvBool.set(1)
        self.sqlSaveCsvChoice = True
        #self.csvBool.trace('w',self.sqlSaveType)
        c = Checkbutton(self.sqlFrame,variable=self.csvBool, text="csv")
        c.grid(row=i,column=3, sticky = tk.W)
        
        i += 1
        
        #text query box
        self.text = Tkinter.Text(self.sqlFrame,borderwidth=10,insertborderwidth=10,padx=5,pady=2, width=50,height=5, highlightbackground="black")
        self.text.grid(row=i,column=0, columnspan=10,rowspan=2)
        i += 9
        
        
        #relative filename input
        entryLabel = Tkinter.Label(self.sqlFrame)
        entryLabel["text"] = "Filename:"
        entryLabel.grid(row=i, column = 0,columnspan=2,stick=tk.E)
        self.queryFilename = Tkinter.StringVar()
        self.queryFilename.set("1.csv")
        entryWidget = Tkinter.Entry(self.sqlFrame, textvariable=self.queryFilename)
        entryWidget.grid(row=i,column=2,columnspan=4)
        
        
        i += 1
        self.sqlFrame.grid(row=0,column=0,sticky=tk.W+tk.N,pady=0)

    def buildCanvas(self):
        
        #self.RightSideCanvas.grid(row=0,column=1,sticky=tk.W)
        # this makes the canvas the same size as the window, but it could be smaller
        self.sniffFrame = tk.Frame( self.RightSideCanvas, width=self.ControlsDx, height=self.ControlsDy)
        i = 0
    
        
        
        #filters
        entryLabel = Tkinter.Label(self.sniffFrame,  font = self.BOLDFONT)
        entryLabel["text"] = "Filters:"
        entryLabel.grid(row=i,column=0, sticky=tk.W)
        
        
        
        i += 1
        self.filterIDs = []
        entryLabel = Tkinter.Label(self.sniffFrame)
        entryLabel["text"] = "Buffer 0:"
        entryLabel.grid(row=i,column =0, sticky=tk.W )
        for j in range(0,2):
            stdID = Tkinter.StringVar()
            stdID.set("")
            entryWidget = Tkinter.Entry(self.sniffFrame, textvariable=stdID)
            self.filterIDs.append(stdID)
            entryWidget["width"] = 5
            entryWidget.grid(row=i,column=j+1, sticky=tk.W)
            
        i += 1
        entryLabel = Tkinter.Label(self.sniffFrame)
        entryLabel["text"] = "Buffer 1:"
        entryLabel.grid(row=i,column =0 ,sticky=tk.W)
        for j in range( 0,4):
            stdID = Tkinter.StringVar()
            stdID.set("")
            entryWidget = Tkinter.Entry(self.sniffFrame, textvariable=stdID)
            self.filterIDs.append(stdID)
            entryWidget["width"] = 5
            entryWidget.grid(row=i,column=j+1, sticky=tk.W)
        clearButton = tk.Button( self.sniffFrame, text="Clear", command=self.clearFilters, width=5)
        clearButton.grid(row=i,column=j+2,sticky=tk.W)
        i += 1
        
        #sniff button
        entryLabel = Tkinter.Label(self.sniffFrame, font = self.BOLDFONT)
        entryLabel["text"] = "Sniff: "
        entryLabel.grid(row=i, column=0, sticky = tk.W)
        sniffButton = tk.Button( self.sniffFrame, text="Start", command=self.sniff, width=3 )
        sniffButton.grid(row=i,column=1, sticky= tk.W)
       
        options = ['Rolling','Fixed']
        self.SniffChoice = Tkinter.StringVar()
        self.SniffChoice.set(options[0])
        optionsSniff = OptionMenu(self.sniffFrame, self.SniffChoice,*tuple(options)) #put an options menu for type
        optionsSniff.grid(row=i,column=2,columnspan=2,sticky=tk.W)
        self.fixedView = False
    
        self.saveInfo = tk.IntVar()
        self.saveInfo.set(1)
        c = Checkbutton(self.sniffFrame, variable=self.saveInfo, text="Save Data")
        c.grid(row=i,column=4,columnspan = 2, sticky=tk.W)
        i += 1
        
        #time to sniff for
        entryLabel = Tkinter.Label(self.sniffFrame)
        entryLabel["text"] = "Time (s):"
        entryLabel.grid(row=i,column=0, sticky=tk.W)
        self.time = Tkinter.StringVar();
        self.time.set("10")
        entryWidget = Tkinter.Entry(self.sniffFrame, textvariable=self.time)
        entryWidget.grid(row=i,column=1, sticky=tk.W)
        entryWidget["width"] = 5
        i += 1
        
        #comment
        entryLabel = Tkinter.Label(self.sniffFrame)
        entryLabel["text"] = "Comment:"
        entryLabel.grid(row=i,column=0, sticky = tk.W)
        self.comment = Tkinter.StringVar();
        self.comment.set("")
        entryWidget = Tkinter.Entry(self.sniffFrame, textvariable=self.comment)
        entryWidget.grid(row=i,column=1, columnspan = 7, sticky=tk.W)
        entryWidget["width"] = 30
        i += 1
        
        #description
        #entryLabel = Tkinter.Label(self.sniffFrame)
        #entryLabel["text"] = "description (csv):"
        #entryLabel.grid(row=i,column=0,columnspan=2, sticky= tk.W)
        #self.description = Tkinter.StringVar();
        #self.description.set("")
        #entryWidget = Tkinter.Entry(self.sniffFrame, textvariable=self.description)
        #entryWidget.grid(row=i,column=2, columnspan = 7, sticky=tk.W)
        #entryWidget["width"] = 30
        #i += 1
        
#        self.fileBool = IntVar()
#        self.fileBool.set(0)
#        c = Checkbutton(self.sniffFrame, variable = self.fileBool, command = self.fileCallback)
#        c.grid(row=i, column = 0)
#        i += 1
#        
        #writing
        entryLabel = Tkinter.Label(self.sniffFrame,  font = self.BOLDFONT)
        entryLabel["text"] = "Write:"
        entryLabel.grid(row=i,column=0, sticky = tk.W)
        
        writeButton = tk.Button( self.sniffFrame, text="Start", command=self.write, width=3 )
        writeButton.grid(row=i,column=1, sticky= tk.W)
        
        # This will hold the data options for writing 
        self.writeData = {}
        
        rtr = IntVar()
        rtr.set(0)
        self.writeData["rtr"] = rtr
        c = Checkbutton(self.sniffFrame,variable=rtr, text="rtr")
        c.grid(row=i,column=2, sticky = tk.W)
        
        fromFile = tk.IntVar()
        fromFile.set(0)
        self.writeData['fromFile'] = fromFile
        c = Checkbutton(self.sniffFrame, variable=fromFile, text="Write from File")
        c.grid(row=i,column=3,columnspan = 2, stick=tk.W)
        
        i += 1
        
        entryLabel = Tkinter.Label(self.sniffFrame, text="Period (ms): ")
        entryLabel.grid(row=i,column=0,sticky=tk.W)
        varTemp = Tkinter.StringVar()
        self.writeData["period"] = varTemp
        varTemp.set(100);
        entryWidget = Tkinter.Entry(self.sniffFrame,width=5,textvariable=varTemp)
        entryWidget.grid(row=i,column=1,sticky=tk.W)
        
        entryLabel = Tkinter.Label(self.sniffFrame, text="Writes: ")
        entryLabel.grid(row=i,column=2,sticky=tk.W)
        
        varTemp = Tkinter.StringVar()
        self.writeData["writes"] = varTemp
        varTemp.set(10)
        entryWidget = Tkinter.Entry(self.sniffFrame, width=5, textvariable=varTemp)
        entryWidget.grid(row=i, column=3, sticky=tk.W)
        
        
        
        
        i += 1
        
        
        
        entryLabel = Tkinter.Label(self.sniffFrame)
        entryLabel["text"] = "sID:"
        entryLabel.grid(row=i,column=0, sticky= tk.W)
        varTemp = Tkinter.StringVar()
        self.writeData['sID'] = varTemp
        varTemp.set("")
        entryWidget = Tkinter.Entry(self.sniffFrame, textvariable=varTemp)
        entryWidget.grid(row=i,column=1, sticky=tk.W)
        entryWidget["width"] = 5
        i += 1
        
        k = 0
        for j in range (0, 8, 2):
            entryLabel = Tkinter.Label(self.sniffFrame)
            entryLabel["text"] = "db%d:" %k
            entryLabel.grid(row=i,column=j, sticky= tk.W)
            varTemp = Tkinter.StringVar()
            self.writeData['db%d'%(k)] = varTemp
            varTemp.set("")
            entryWidget = Tkinter.Entry(self.sniffFrame, textvariable=varTemp)
            entryWidget.grid(row=i,column=j+1, sticky=tk.W)
            entryWidget["width"] = 5
            k += 1
            print k
            
        for j in range(0,8,2):
            entryLabel = Tkinter.Label(self.sniffFrame)
            entryLabel["text"] = "db%d:" %((k))
            entryLabel.grid(row=i+1,column=j, sticky= tk.W)
            varTemp = Tkinter.StringVar()
            self.writeData['db%d'%((k))] = varTemp
            varTemp.set("")
            entryWidget = Tkinter.Entry(self.sniffFrame, textvariable=varTemp)
            entryWidget.grid(row=i+1,column=j+1, sticky=tk.W)
            entryWidget["width"] = 5
            k +=1
    
        i += 2
       
        
        #expand it to the size of the window and fill
        #self.sniffFrame.pack( expand=tk.YES, fill=tk.BOTH)
        #self.sniffFrame.pack(side=tk.RIGHT,expand=tk.YES, fill=tk.BOTH)
        self.sniffFrame.grid(row=0,column=0,sticky=tk.W+tk.N,pady=0)
        #canvas2 = tk.Canvas(self.RightSideCanvas, width=self.ControlsDx, height=self.ControlsDy)
        #canvas2.grid(row=0,column=0,sticky=tk.W+tk.N, pady=0)
        #self.sniffFrame.lift(aboveThis=canvas2)
        #tk.Misc.lift(self.sniffFrame, aboveThis=None)
        #self.sniffFrame.lift(canvas2)
        
        
        return

    def buildDataCanvas(self):
        self.dataFrame = tk.Canvas(self.root, width=self.dataDx, height=self.dataDy)
        #self.dataFrame.grid(row=0,column=0,sticky=tk.W)
        self.dataFrame.pack(side=tk.LEFT,padx=2,pady=2,fill=tk.Y)
        
        
        #separator line
        sep = tk.Frame(self.root, height=self.dataDy,width=2,bd=1,relief=tk.SUNKEN)
        sep.pack(side=tk.LEFT,padx=2,pady=2,fill=tk.Y)
        
        self.infoFrame = tk.Frame(self.dataFrame,width=self.dataDx,height=20)
        self.infoFrame.pack(side=tk.BOTTOM, padx=2,pady=2,fill=tk.X)
        
        sep = tk.Frame(self.dataFrame,height=2,width=self.dataDx,bd=1,relief=tk.SUNKEN)
        sep.pack(side=tk.BOTTOM,padx=2,pady=2,fill=tk.X)
        
        self.statusString = tk.StringVar()
        self.statusString.set("Not Connected")
        label = tk.Label(self.infoFrame,text="Status: ")
        label.grid(row=0,column=0,sticky=tk.W)
        self.statusLabel = tk.Label(self.infoFrame,textvariable=self.statusString, bg="red")
        self.statusLabel.grid(row=0,column=1,sticky=tk.W)
        self.msgCount = tk.StringVar()
        self.msgCount.set("0")
        self.msgPrev = time.time()
        label = tk.Label(self.infoFrame,text="Count: ")
        label.grid(row=0,column=2, sticky=tk.W)
        label = tk.Label(self.infoFrame,textvariable=self.msgCount, width=5)
        label.grid(row=0,column=3,sticky=tk.W)
        
        self.msgDelta = tk.StringVar()
        self.msgDelta.set("0")
        label = tk.Label(self.infoFrame,text='Delta T: ')
        label.grid(row=0,column=4,sticky=tk.W)
        label = tk.Label(self.infoFrame, textvariable=self.msgDelta)
        label.grid(row=0,column=5, sticky=tk.W)
    
        
        self.topFrame = tk.Frame(self.dataFrame,width=self.dataDx,height=4)
        self.topFrame.pack(side=tk.TOP, padx=2,pady=2,fill=tk.X)
        label = tk.Label(self.topFrame)
        label["text"] = "\t\t\t    db0 db1 db2 db3 db4 db5 db6 db7  deltaT";
        
        label.pack(side=tk.LEFT)
        
        
        
        
        
        self.dataText = tk.Text(self.dataFrame,background='white', width=self.dataDx, wrap=Tkinter.WORD)
        self.dataText.config(state=DISABLED)
        self.scroll = Scrollbar(self.dataFrame)
        self.scroll.pack(side=tk.RIGHT,fill=tk.Y)
        self.dataText.configure(yscrollcommand=self.scroll.set)
        #self.scroll.pack(side=tk.RIGHT,fill=tk.Y)
        self.scroll.config(command=self.dataText.yview)
        self.dataText.pack(side=tk.LEFT,fill=tk.Y)
        
        self.hyperlink = tkHyperlinkManager.HyperlinkManager(self.dataText)
        
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
        self.buttons.append( ( 'sniff', tk.Button(self.cntlframe, text="Sniff", command=self.sniffFrameLift,width=10)))
        self.buttons[-1][1].pack(side=tk.LEFT)
        self.buttons.append( ( 'cmd1', tk.Button( self.cntlframe, text="Experiments", command=self.experimentFrameLift, width=10 ) ) )
        self.buttons[-1][1].pack(side=tk.LEFT)
        self.buttons.append( ( 'SQL', tk.Button( self.cntlframe, text="SQL", command=self.sqlFrameLift, width=10)))
        self.buttons[-1][1].pack(side=tk.LEFT)
        self.buttons.append( ('cmd3', tk.Button(self.cntlframe, text="ID Information", command=self.infoFrameLift, width=15)))
        self.buttons[-1][1].pack(side=tk.LEFT)
        return

    #Bind callbacks with the keyboard/keys
    def setBindings(self):
        """
        This method will set bindings on the window. This includes mouse clicks and key presses
        """
        #self.root.bind( '<Button-1>', self.handleButton1 )
        #self.root.bind( '<Button-2>', self.handleButton2 )
        #self.root.bind( '<Button-3>', self.handleButton3 )
        #self.root.bind( '<B1-Motion>', self.handleButton1Motion )
        self.root.bind( '<Command-q>', self.handleModQ )
        self.root.bind( '<Control-z>', self.handleSettings)
        #self.root.bind( '<Command-o>', self.handleModO )
        self.root.bind( '<Control-q>', self.handleQuit )
        self.root.bind( '<Control-s>', self.sniffFrameLift)
        self.root.bind( '<Control-e>', self.experimentFrameLift)
        self.root.bind( '<Control-u>', self.sqlFrameLift)
        #self.root.bind('<Return>',self.handleStim )
        #self.root.bind('<Key>',self.handleKeys)

    # this method handles inputs when the user presses a key
    def handleKeys(self,event):
        print event.char
    
    #quits the GUI
    def handleQuit(self, event=None):
        """ 
        This method is called when the user quits the program. It terminates the display and exits
        """
        print 'Terminating'
        self.root.destroy()
             
    def setDataManage(self,table, name, host, username, password, database):
        """
        This method will update the stored information for accessing the MYSQL database. The settings will be 
        saved to the settings file.
        
        @type table: string
        @param table: SQL table to add data to
        @type name: string
        @param name: Name for SQL account
        @type host: string
        @param host: Host for MYSQL table
        @type username: string
        @param username: MYSQL username
        @type password: string
        @param password: MYSQL username password
        @type database: string
        @type database: database we want to use
        
        """
        print "Updating MYSQL database information"
        
        self.SQL_NAME = name
        self.writeiniFile(self.SETTINGS_FILE, "DataManager", "sql_name", name)
        self.SQL_HOST = host
        self.writeiniFile(self.SETTINGS_FILE, "DataManager", "sql_host", host)
        self.SQL_USERNAME = username
        self.writeiniFile(self.SETTINGS_FILE, "DataManager", "sql_username", username)
        self.SQL_PASSWORD = password
        self.writeiniFile(self.SETTINGS_FILE, "DataManager", "sql_password", password)
        self.SQL_DATABASE = database
        self.writeiniFile(self.SETTINGS_FILE, "DataManager", "sql_database", database)
        self.SQL_TABLE = table
        self.writeiniFile(self.SETTINGS_FILE, "DataManager", "sql_table", table)
        self.dm = DataManage(host=self.SQL_HOST, db=self.SQL_DATABASE,username=self.SQL_USERNAME,password=self.SQL_PASSWORD,table=self.SQL_TABLE,dataLocation=self.DATA_LOCATION)


    def handleSettings(self, event=None):
        """
        This method will open the settings dialog box for the user to change various components of the GUI.
        """
        data = {}
        dialogBox =  settingsDialog(parent = self.root, dClass = self, data=data, title = "Settings")
        
    #quits
    def handleModQ(self, event):
        """ 
        This method will quit the GUI
        """
        self.handleQuit()

    # writes a row of data to the end of a csv file that is given by filename
    #def writeRow(self,data,filename):
    #    writeFile  = open(filename,'a')
    #    dataWriter = csv.writer(writeFile,delimiter=',')
    #    dataWriter.writerow(data)
    #    writeFile.close()
    #    return
   
    def fileCallback(self):
        if( self.fileBool == 0):
            pass

    def setRunning(self):
        """
        This method sets the running boolean when a method is communicating with the bus
        """
        self.running.set(1)
    
    def unsetRunning(self):
        """
        This method unsets the running boolean when a method is done communicating with the bus
        """
        self.running.set(0)

    def getRate(self):
        """
        This method returns the rate that the GOODTHOPTER10 is set to
        """
        return self.freq

    def connectBus(self):
        """ 
        This method will try to reconnect with the GOODTHOPTER10. It will first check to make sure that no
        method is currently communicating with the bus. 
        """
        if( self.running.get() == 1):
            return
        try:
            self.comm = experiments(self.DATA_LOCATION)
            print "connected"
            self.statusString.set("Ready")
            self.statusLabel.config(bg="green")
        except:
            print "Board not properly connected. please plug in the GoodThopter10 and re-attempt"
            self.comm = None

    def checkComm(self):
        """
        This method check to see if the program is able to begin communication with the GOODTHOPTER10 board. This method
        should be called before anything begins to try and communicate. It will check first to see if the board is connected
        and will then check to see if the self.running boolean is set or not.
        
        @rtype: Boolean
        @return: False if the board is either not connected or if there is currently a script communicating with the board. True otherwise
        """
        if(not self.isConnected() ):
            print "GoodThopter10 not connected. Please connect board"
            return False
        
        elif( self.running.get() == 1 ):
            print  "There is a current script running. Please wait until it has finished"
            return False
        
        return True
    
    def getDataLocation(self):
        """
        Returns the path to the data location
        @rtype: string
        @return: Data location path
        """
        return self.DATA_LOCATION
    
    def setDataLocation(self, location):
        """
        Sets the data location path in the program as well as saved to the settings file.
        @type location: string
        @param location: path to new location to save data to
        """
        print "Updating Data Location"
        self.writeiniFile(self.SETTINGS_FILE, "FileLocations", "data_location", location)
        self.DATA_LOCATION = location
        
    
    #set the rate on the MC2515
    def setRate(self,freq):
        """
        This method will set the rate that the board communicates with  the CAN Bus on. 
        @type freq: number
        @param freq: Frequency of CAN communication
        """
        print "Updating Bus Rate"
        if( not self.checkComm()):
            return
        self.writeiniFile(self.SETTINGS_FILE, "BusInfo", "frequency", freq)
        self.comm.setRate(freq)
        self.freq = freq
        
    # This method will clear all the filter inputs for the user
    def clearFilters(self):
        """
        This method will clear the filters that the user has input into the dialog spots. It does not reset the chip
        and clear them on the board.
        """
        for element in self.filterIDs:
            element.set("")
    
    
    def sniff(self):
        """ This method will sniff the CAN bus. It will take in the input arguments from the GUI and pass them onto the
        sniff method in the L{GoodFETMCPCANCommunication.sniff} file. The method will take in any filters that have been
        set on the GUI, as well as the sniff length and comment off the display. This method will call L{sniffControl} which
        will be run as a thread.
        """
        if( not self.checkComm() ):
            return
        # get time and check that it is correct
        try:
            time = int(self.time.get())
        except:
            print "time in seconds as an integer"
        comments = self.comment.get()
        description = comments
        #description = self.description.get()
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
        
        #figure out if the data gathered will be saved
        if( self.saveInfo.get() == 1):
            writeToFile = True
        else:
            writeToFile = False
        
        self.data = Queue.Queue()
    
        self.deltas = {}
        #sniff
        #self.comm.sniff(freq=self.freq,duration=time,
        #          description=description,verbose=self.verbose,comment=comments,filename = None,
        #           standardid=standardid, debug = False)    
        #self.running = True
        #thread.start_new_thread(self.comm.sniff, (self.freq, time, description, True, comments, None, standardid, False, False, True, self.data ))
        thread.start_new_thread(self.sniffControl, (self.freq, time, description, False, comments, None, standardid, False, False, True, self.data, writeToFile ))
        #self.sniffControl(self.freq, time, description, False, comments, None, standardid, False, False, True, self.data)
        #self.root.after(50, self.updateCanvas)
        
        self.running.set(0) # we are running a method with the bus
        
        
        
    def sniffControl(self,freq,duration,description, verbose=False, comment=None, filename=None, standardid=None, debug=False, faster=False, parsed=True, data = None, writeToFile = True):
        """
        This method will actively do the sniffing on the bus. It will call the sniff method in the GoodFETMCPCANCommunication class. This method will
        be called by the L{sniff} method when started by the user in the GUI. It will set up the display for the incoming sniffed data as well as 
        reset the counters. The input parameters to this method are the same as to the sniff method in the GoodFETMCPCANCommunication class.
        
        @type freq: number
        @param freq: Frequency of the CAN communication
        @type description: string
        @param description: This is the description that will be put in the csv file. This gui will set this to be equal to the comments string
        @type verbose: Boolean
        @param verbose: This will trigger the sniff method to print out to the terminal. This is false by default since information is printed to the GUI. 
        @type comment: string
        @param comment: This is the comment tag for the observation. This will be saved with every sniffed packet and included in the data uploaded to the SQL database
        @type filename: String
        @param filename: filename with path to save the csv file to of the sniffed data. By default the sniff method in the GoodFETMCPCANCommunication file will automatically deal with
                         the file management and this can be left as None.
        @type standardid: List of integers
        @param standardid: This will be a list of the standard ids that the method will filter for. This can be a list of up to 6 ids.
        @type debug: Boolean
        @param debug: 
        
        """
        
        #reset msg count
        self.msgCount.set("0")
        self.msgDelta.set("0")
        self.msgPrev = time.time()
        self.dataText.config(state=tk.NORMAL)
        self.dataText.delete(1.0, END)
        self.dataText.config(state=tk.DISABLED)
        #self.running = True
        self.setRunning()
        self.updateID = self.root.after(50,self.updateCanvas)
        count = self.comm.sniff(self.freq, duration, description, verbose, comment, filename, standardid, debug, faster, parsed, data, writeToFile)
        self.unsetRunning()
        #self.root.after_cancel(self.updateID)
     
    def updateStatus(self,name,index,mode):
        runningVal = self.running.get()
        if( runningVal == 1):
            self.statusString.set("Running")
            self.statusLabel.config(bg = "yellow")
        if( runningVal == 0):
            if( self.comm != None):
                self.statusString.set("Ready")
                self.statusLabel.config(bg="green")
        
    
    def updateCanvas(self):
        choice = self.SniffChoice.get()
        if( choice == 'Rolling' and self.fixedView == True):
            self.fixedView = False
            self.delta = {}
            self.dataText.config(state=tk.NORMAL)
            self.dataText.delete(1.0,END)
            self.dataText.config(state=tk.DISABLED)
        elif( choice == 'Fixed' and self.fixedView ==False):
            self.fixedView = True
            self.delta = {}
            self.dataText.config(state=tk.NORMAL)
            self.dataText.delete(1.0,END)
            self.dataText.config(state=tk.DISABLED)
        #print "called"
        #print self.dataLength
        #print self.data
        #print self.data.empty()
        while(not self.data.empty()):
            #print "trying to add"
            #print self.data[self.dataLength]
            try:
                packet = self.data.get_nowait()
                #packet = self.data.get(block=False)
                #print "I GOT  THTIS: ", packet
            except Queue.Empty:
                pass
            else:
                sID = packet.get('sID')
                if( self.deltas.get(sID) == None):
                    print "cannot find id"
                    self.deltas[sID] = {'time':packet.get("time")} #create a new dictionary for the arb id
                    sIDDic = self.deltas.get(sID)
                    delta = -1
                else:
                    sIDDic = self.deltas.get(sID);
                    
                    delta = packet['time'] - sIDDic['time'] #get the delta time
                    sIDDic['time'] = packet['time']
                    #rint delta
                #time = packet.get("time")
                rtr = packet.get('rtr')
                length = packet.get('length')
                data = ""
                for i in range(0,length):
                    dbidx = 'db%d'%i
                    data += " %03d"%packet[dbidx]
                    #data += " %03d"% ord(packet[dbidx])
                #get position of the scrollbar
                position = self.scroll.get()[1]
                positionT = self.dataText.yview()[0]
                #fixedView = True
                if( self.fixedView == True):
                    #we need to add the arbID (doesn't already exist)
                    lineNum = sIDDic.get('lineNum')
                    if( lineNum == None):
                        numlines = self.dataText.index('end - 1 line').split('.')[0] #get number of lines
                        print numlines
                        sIDDic['lineNum'] = float(numlines)
                        lineNum = float(numlines)
                    else:
                        self.dataText.config(yscrollcommand=None, state=NORMAL)
                        self.dataText.delete(lineNum, lineNum+1) #delete the previous entry for this id
                    self.dataText.config(yscrollcommand=None, state=NORMAL)
                    #self.dataText.insert(lineNum,"arbID: ")
                    #self.dataText.insert(lineNum, "%04d"%sID, self.hyperlink.add(self.arbIDInfo,sID))
                    self.dataText.insert(lineNum, (" Length: %d rtr: %d "%(length,rtr)) + data + (" DeltaT: %04f\n"%delta))
                    self.dataText.insert(lineNum, "%04d"%sID, self.hyperlink.add(self.arbIDInfo,sID))    
                    self.dataText.insert(lineNum,"arbID: ");
                        
                else:
                    self.dataText.config(yscrollcommand=None, state=NORMAL)
                    self.dataText.insert(END,"arbID: ")
                    self.dataText.insert(END, "%04d"%sID, self.hyperlink.add(self.arbIDInfo,sID))
                    self.dataText.insert(END, (" Length: %d rtr: %d "%(length,rtr)) + data + (" DeltaT: %04f\n"%delta))
                    #self.dataText.insert(END,packet+"\n")
                self.text.yview(END)
                self.dataText.config(yscrollcommand=self.scroll.set, state=DISABLED)
                #if the position was at the end, update it now now be at the end again
                #self.scroll.set(1.0,0)
                if (position ==1.0):
                    self.dataText.yview(END)
                #print "position ", position
                #self.dataText.yview(tk.MOVETO, 1.0)
                self.msgDelta.set("%04f"%(packet['time']-self.msgPrev))
                self.msgPrev = packet['time']
                self.msgCount.set("%d"%(int(self.msgCount.get())+1))
            #self.dataLength += 1
        if(self.running.get() == 1):
           self.updateID = self.root.after(50,self.updateCanvas)
        
  
            
    def callback(self):
        self.arbIDInfo(id)
            
    def arbIDInfo(self,id):
        print "Request for information on %d" %id
        
    def write(self):
        if( not self.checkComm()):
            return
        packet = []
        if(self.writeData["fromFile"].get() == 1):
            # ping the user to choose the file for writing
            filename = askopenfilename(title="Choose a File to Load Packet Data")
            data = self.dm.readWriteFileDEC(filename)
            #check that we have data
            if( data == None):
                print "Failed to load file"
                return
            #write the data
            self.comm.writeData(data,self.freq)
            return
        #otherwise gather data from the GUI for writing
        else:
            try:
                sID = int(self.writeData["sID"].get())
                print "here1"
                writes = int(self.writeData["writes"].get())
                if(writes == 0):
                    repeat = False
                else:
                    repeat = True
                #print "sid"
                periodStr = self.writeData["period"].get()
                if( periodStr == ""):
                    period = None
                else:
                    period = float(periodStr)
                   
                #print "attempts"
                #print self.writeData
                if( self.writeData["rtr"].get() == 1):
                    packet = None
                else:
                    for j in range(0,8):
                        #print "db%d"%j
                        var = self.writeData.get("db%d"%j)
                        packet.append(int(var.get()))
            except:            
                tkMessageBox.showwarning('Invalid Input', 'Incorrectly formatted input. Values are not Integers')
                print "Invalid input!"
                return
                
        #self.comm.spitSetup(self.freq)
        #for i in range(0,attempts):
        #self.comm.spit(self.freq,[sID],repeat, writes, period=period, debug=False, packet=packet)
        thread.start_new_thread( self.writeControl, (self.freq,[sID], repeat, writes, period, False, packet))
     
     
     # This is the method that will be called as a thread to write to the bus
    def writeControl(self, freq, sID, repeat, writes, period, debug=False, packet=None):  
         self.comm.spitSetup(self.freq)
         self.setRunning()
         self.comm.spit(self.freq,sID,repeat, writes, period=period, debug=False, packet=packet)
         self.unsetRunning()
              
            
        #print "write Packet?"
        
    def uploaddb(self):
        msg = "Upload data to table: %s, \n you are at frequency: %.2f"%(self.SQL_TABLE,self.freq)
        response = tkMessageBox.askyesno(title = "Upload Data", message = msg)
        
        if(response):
            print "Uploading all files"
            self.dm.uploadFiles()
    
    def infoFrameLift(self, event=None):
        tk.Misc.lift(self.blankCanvas,aboveThis=None)
        tk.Misc.lift(self.infoFrame,aboveThis=None)
            
    def sqlFrameLift(self, event=None):
        tk.Misc.lift(self.blankCanvas,aboveThis=None)
        tk.Misc.lift(self.sqlFrame,aboveThis=None)
        
    def sniffFrameLift(self, event=None):
        #tk.Misc.lower(self.experimentFrame, belowThis=self.blankCanvas)
        #tk.Misc.lift(self.sniffFrame, aboveThis=self.blankCanvas)
        tk.Misc.lift(self.blankCanvas,aboveThis=None)
        tk.Misc.lift(self.sniffFrame, aboveThis=None)
    def experimentFrameLift(self, event=None):
        #data = {}
        #thread.start_new_thread(experiments,(self.root, self, self.comm,data,"Experiments"))
        #exp = experimentsGUI(self.root, self, comm=self.comm, data = data, title = "Experiments")
        #tk.Misc.lower(self.sniffFrame, belowThis=self.blankCanvas)
        #tk.Misc.lift(self.experimentFrame, aboveThis=self.blankCanvas)
        tk.Misc.lift(self.blankCanvas,aboveThis=None)
        tk.Misc.lift(self.experimentFrame,aboveThis=None)
        #pass
        
        
    def idInfo(self):
        """ This method will open an info box for the user
            to gain information on a known arbID"""
        infoBox = info(parent=self.root, title="Information Gathered")
        pass
        
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
        if( self.csvBool.get() == 1):
            self.dm.writeDataCsv(data,filename)
        else:
            self.dm.writetoPcapfromSQL(filenameWriteto=filename,results=data)
          
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
    
    def generalFuzz(self):
        if( not self.checkComm()):
            return
        try:
            Fuzzes = int(self.generalFuzzData["Fuzzes"].get())
            period = float(self.generalFuzzData["period"].get())
            writesPerFuzz = int(self.generalFuzzData["writesPerFuzz"].get())
        except:            
            tkMessageBox.showwarning('Invalid Input', 'Incorrectly formatted input. Values are not Integers')
            print "Invalid Input. Please check input and try again"
            return
        
        thread.start_new_thread(self.generalFuzzControl, (self.getRate(),Fuzzes,period,writesPerFuzz))
        
    def generalFuzzControl(self, freq,Fuzzes, period, writesPerFuzz):
        self.setRunning()
        self.comm.generalFuzz(freq,Fuzzes,period,writesPerFuzz)
        self.unsetRunning()
        
    def packetResponse(self):
        if( not self.checkComm()):
            return
        try:
            time = int(self.packetResponseData['time'].get())
            repeats = int(self.packetResponseData['repeats'].get())
            period = float(self.packetResponseData["period"].get())
            responseID = int(self.packetResponseData['responseID'].get())
            listenID = int(self.packetResponseData['listenID'].get())
            responsePacket = []
            listenPacket = []
            for k in range(0,8):
                idx_listen = 'Listen_db%d'%k
                idx_response = 'Response_db%d'%k
                listenStr = self.packetResponseData[idx_listen].get()
                if( listenStr == ""):
                    listenPacket = None
                else:
                    listenPacket.append(int(listenStr))
                        
                #listenPacket.append(int(self.packetResponseData[idx_listen].get()))
                responsePacket.append(int(self.packetResponseData[idx_response].get()))
                    
        except:
            tkMessageBox.showwarning('Invalid Input', 'Incorrectly formatted input.')
            returns
         #   print "Invalid Input. Please check input and try again."
         #   return
        
        #self.comm.packetRespond(self.dClass.getRate(), time,repeats,period,responseID,responsePacket,listenID,listenPacket)
        thread.start_new_thread(self.packetResponseControl, (self.getRate(), time,repeats,period,responseID,responsePacket,listenID,listenPacket))
        
    def packetResponseControl(self, freq, time, repeats, period,  responseID, respondPacket,listenID, listenPacket = None):
        self.setRunning()
        self.comm.packetRespond(freq, time,repeats,period,responseID,respondPacket,listenID,listenPacket)
        self.unsetRunning()
        
    def reInjectFuzzed(self):
        
        if( not self.checkComm()):
            return
        try:
            date = self.reInjectData["date"].get();
            if( date == ""):
                raise Exception
            startTimestr = self.reInjectData['startTime'].get()
            if( startTimestr == ""):
                startTime = None
            else:
                #startTime = int(startTimestr)
                #put it into time stamp format: tuple( year, month, day, hour, min, sec, wday,yday,isdst) -- leave the last ones 0
                startTime = time.mktime((int(date[0:4]), int(date[4:6]), int(date[6:8]), int(startTimestr[0:2]), int(startTimestr[2:4]),0,0,0,0))
            endTimestr = self.reInjectData['endTime'].get()
            if( endTimestr == ""): #if they did not input an end time (optional)
                endTime = None
            else:
                
                endTime = time.mktime((int(date[0:4]), int(date[4:6]), int(date[6:8]), int(endTimestr[0:2]), int(endTimestr[2:4]),0,0,0,0))
            idstr = self.reInjectData['sID'].get()
            if( idstr == ""): # they did not input an id (optional)
                id = None
            else:
                id = int(idstr)  
            
        except:
            tkMessageBox.showwarning('Invalid Input', 'Incorrectly formatted input.')
            print "Invalid Input!"
            return
        injectLocation = self.dm.getInjectedLocation()
        filename = injectLocation + date + "_GenerationFuzzedPackets.csv"
        print "filename ", filename
        print "date ", date
        print "id ", id
        print " startTime ", startTime
        print " endTime ", endTime
        # start a new thread
        thread.start_new_thread(self.reInjectFuzzedControl, (filename, float(startTime), float(endTime),id))
        
        
    def reInjectFuzzedControl(self, filename, startTime,endTime,id):
        self.setRunning()
        #load the data from the file
        data = self.dm.readInjectedFileDEC(filename,startTime,endTime,id)
        #inject the data 
        self.comm.writeData(data,self.freq)
        self.unsetRunning()
        
        
    def GenerationFuzz(self):
        
        print "Generation Fuzz"
        if( not self.checkComm()):
            return
        #sIDs = int(self.fuzzData['sID'].get())
        try:
            ids = self.fuzzData['sIDs'].get().split(",")
            sID = []
            for id in ids:
                sID.append(int(id))
            period = int(self.fuzzData['period'].get())
            writesPerFuzz = int(self.fuzzData['writesPerFuzz'].get())
            Fuzzes = int(self.fuzzData['Fuzzes'].get())
            dbInfo = {}
            for i in range(0,8):
                idx = 'db%d'%i
                dbValues = self.fuzzData.get(idx)
                dbInfo[idx] = [int(dbValues[0].get()), int(dbValues[1].get())]
        except:
            print "Invalid Input."
            tkMessageBox.showwarning('Invalid Input', 'Incorrectly formatted input.')
            return
        #start the writing as a thread
        self.GenerationFuzzControl(self.getRate(),sID,dbInfo,period,writesPerFuzz,Fuzzes)
        #thread.start_new_thread(self.GenerationFuzzControl,(self.getRate(),sID, dbInfo,period,writesPerFuzz,Fuzzes))
        
    def GenerationFuzzControl(self,freq, sID, dbInfo, period, writesPerFuzz, Fuzzes):
        self.setRunning()
        self.comm.generationFuzzer(freq, sID,dbInfo, period, writesPerFuzz, Fuzzes)
        self.unsetRunning()
        
    def RTRsweepID(self):
        print "Sweep across given IDs requesting packets"
        if( not self.checkComm()):
            return
        sniffTime = self.sniffTime.get()
        low = self.lowSweep.get()
        high = self.HighSweep.get()
        attempts = self.attempts.get()
        verbose = True
        try: 
            sT = int(sniffTime)
            lowI = int(low)
            highI = int(high)
            attemptsI = int(attempts)
        except:
            tkMessageBox.showwarning('Invalid Input', 'Incorrectly formatted input. Values are not Integers')
            print "Values are not integers. Please check inputs and try again."
            return
        thread.start_new_thread(self.RTRsweepIDControl, (self.getRate(), lowI,highI,attemptsI,sT,verbose))
 
    def RTRsweepIDControl(self, freq, lowI, highI,attemptsI, sT, verbose):
        self.setRunning()
        #thread.start_new_thread(self.comm.rtrSweep,(self.dClass.getRate(), lowI, highI, attemptsI, sT, verbose))
        self.comm.rtrSweep(freq, lowI, highI, attemptsI, sT, verbose)
        self.unsetRunning()
 
    def sweepID(self):
        if( not self.checkComm()):
            return
        sniffTime = self.sniffTime.get()
        low = self.lowSweep.get()
        high = self.HighSweep.get()
        try:
            sT = int(sniffTime)
            lowI = int(low)
            highI = int(high)
        except:
            tkMessageBox.showwarning('Invalid Input', 'Values are not integers. Please check inputs and try again.')
            print "Values are not integers. Please check inputs and try again."
            return
        if( highI < lowI  or sT <= 0):
            print "Incorrectly formated inputs! Please check that lower ID is less than higher ID"
        thread.start_new_thread(self.sweeIDControl, (self.getRate(),lowI,highI,sT))
    
    def sweeIDControl(self, freq, lowI, highI, sT):
        self.setRunning()
        self.comm.filterStdSweep( freq, lowI, highI, sT )
        self.unsetRunning()
    
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
        self.rateChoice.set(self.dClass.getRate());
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
        
        entryLabel = Tkinter.Label(master)
        entryLabel["text"] = "File storage location:"
        entryLabel.grid(row=i,column=0,columnspan=2,sticky=tk.W)
        i += 1
        entryLabel = Tkinter.Label(master)
        entryLabel["text"] = "Path:"
        entryLabel.grid(row=i,column=1,sticky=tk.W)
        self.fileLocation = Tkinter.StringVar()
        self.fileLocation.set(self.dClass.getDataLocation())
        entryWidget = Tkinter.Entry(master, textvariable=self.fileLocation)
        entryWidget.grid(row=i,column=2,columnspan=3,sticky=tk.W)
        entryWidget["width"] = 30
        
    def setRate(self):
        rate = float(self.rateChoice.get())
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
        print "Updating Configurations."
        if not self.validate():
            self.initial_focus.focus_set() #put focus back
            return
        fileLocation = self.fileLocation.get()
        self.dClass.setDataLocation(fileLocation)
        #table = "%s"% self.sqlDB[0].get()
        #print table
        table = self.sqlDB[0].get()
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
    dapp = DisplayApp()
    dapp.main()
