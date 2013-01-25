
# Chris Hoder
# 11/3/2012

import Tkinter
#import the linked list, sniff threading
from node import *
from LL import *
from InfoBox import *
import csv
import time
import sys;
import binascii;
import array;
from DataManage import DataManage
import datetime
import os

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
    def __init__(self, width, height, rate=500, table):
        #configure information
        #Initialize communication class
        self.comm = GoodFETMCPCANCommunication()
        self.freq = 500
        self.verbose = True
        
        # Initialize the data manager
        self.table = table
        self.dm = DataManage(host="thayerschool.org", db="thayersc_canbus",username="thayersc_canbus",password="c3E4&$39",table=self.table)
        
        #store figure
        self.fig = None
        
        #stimulus is initial not being conducted
        self.isStimulus = False
        
        #save the filenames, initialized when sniffing begins
        self.filenames = []

        # create a tk object, which is the root window
        self.root = tk.Tk()

        # width and height of the window
        self.initDx = width
        self.initDy = height

        # set up the geometry for the window
        self.root.geometry( "%dx%d+50+30" % (self.initDx, self.initDy) )

        # set the title of the window
        self.root.title("Add Plots to the graph")

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

        self.yAxesList = []
        # 4 pre programmed colors ( will repeat if more than 4 different 
        # yAxis data is plotted
        self.colorList = ["r","g","b","y"]
        
        
        
    
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
        menutext = [ [ 'Quit  \xE2\x8C\x98-Q' ],
                     [ '-', '-', '-' ] ]

        # menu callback functions
        menucmd = [ [ self.handleQuit],
                    [self.handleCmd1, self.handleCmd2, self.handleCmd3] ]
        
        # build the menu elements and callbacks
        for i in range( len( self.menulist ) ):
            for j in range( len( menutext[i]) ):
                if menutext[i][j] != '-':
                    self.menulist[i].add_command( label = menutext[i][j], command=menucmd[i][j] )
                else:
                    self.menulist[i].add_separator()


    # create the canvas object
    def buildCanvas(self):
        # this makes the canvas the same size as the window, but it could be smaller
        self.canvas = tk.Canvas( self.root, width=self.initDx, height=self.initDy )
        
    
        #allows the user to set the rate
        i = 0
        entryLabel = Tkinter.Label(self.canvas)
        entryLabel["text"] = "Set Rate:"
        entryLabel.grid(row=i,column=0)
        self.rateChoice = tk.StringVar()
        self.rateChoice.set("500");
        self.rateMenu = tk.OptionMenu(self.canvas,self.rateChoice,"83.3","100","125","250","500","1000")
        self.rateMenu.grid(row=i,column=1)
        rateButton = tk.Button(self.canvas,text="Set Rate",command=self.setRate,width=10)
        rateButton.grid(row=i,column=2)
        i += 1
        
        
        #filters
        entryLabel = Tkinter.Label(self.canvas)
        entryLabel["text"] = "Filters:"
        entryLabel.grid(row=i,column=0)
        self.filterIDs = []
        for j in range(0,4):
            stdID = Tkinter.StringVar()
            stdID.set("")
            entryWidget = Tkinter.Entry(self.canvas, textvariable=stdID)
            self.filterIDs.append(stdID)
            entryWidget["width"] = 10
            entryWidget.grid(row=i,column=j+1)
        
        i+=1
        
        #sniff button
        sniffButton = tk.Button( self.canvas, text="Sniff", command=self.sniff, width=10 )
        sniffButton.grid(row=i,column=0)
        i += 1
        
        #time to sniff for
        entryLabel = Tkinter.Label(self.canvas)
        entryLabel["text"] = "Time (s):"
        entryLabel.grid(row=i,column=1)
        self.time = Tkinter.StringVar();
        self.time.set("10")
        entryWidget = Tkinter.Entry(self.canvas, textvariable=self.time)
        entryWidget.grid(row=i,column=2)
        entryWidget["width"] = 10
        i += 1
        
        #comment
        entryLabel = Tkinter.Label(self.canvas)
        entryLabel["text"] = "comment (sql):"
        entryLabel.grid(row=i,column=1)
        self.comment = Tkinter.StringVar();
        self.comment.set("")
        entryWidget = Tkinter.Entry(self.canvas, textvariable=self.comment)
        entryWidget.grid(row=i,column=2)
        entryWidget["width"] = 10
        i += 1
        
        #description
        entryLabel = Tkinter.Label(self.canvas)
        entryLabel["text"] = "description:"
        entryLabel.grid(row=i,column=1)
        self.description = Tkinter.StringVar();
        self.description.set("")
        entryWidget = Tkinter.Entry(self.canvas, textvariable=self.description)
        entryWidget.grid(row=i,column=2)
        entryWidget["width"] = 10
        i += 1
        
#        self.fileBool = IntVar()
#        self.fileBool.set(0)
#        c = Checkbutton(self.canvas, variable = self.fileBool, command = self.fileCallback)
#        c.grid(row=i, column = 0)
#        i += 1
#        
        #writing
        entryLabel = Tkinter.Label(self.canvas)
        entryLabel["text"] = "Write"
        entryLabel.grid(row=i,column=0)
        i += 1
        
       
        #sql
        entryLabel = Tkinter.Label(self.canvas)
        entryLabel["text"] = "SQL Query"
        entryLabel.grid(row=i,column=0)
        i+= 1
        
        #text query box
        self.text = Tkinter.Text(self.canvas,borderwidth=10,insertborderwidth=10,padx=5,pady=2, width=50,height=10, highlightbackground="black")
        self.text.grid(row=i,column=0, columnspan=8,rowspan=5)
        i += 9
        self.pcapBool = IntVar()
        self.pcapBool.set(0)
        c = Checkbutton(self.canvas, variable = self.pcapBool)
        c.grid(row=i,column=0)
        entryLabel = Tkinter.Label(self.canvas)
        entryLabel["text"] = "pcap"
        entryLabel.grid(row=i, column = 1)
                        
        self.csvBool = IntVar()
        self.csvBool.set(1)
        c = Checkbutton(self.canvas,variable=self.csvBool)
        c.grid(row=i,column=2)
        entryLabel = Tkinter.Label(self.canvas)
        entryLabel["text"] = "csv"
        entryLabel.grid(row=i, column = 3)
        i += 1
        
        #relative filename input
        entryLabel = Tkinter.Label(self.canvas)
        entryLabel["text"] = "Filename:"
        entryLabel.grid(row=i, column = 0)
        self.queryFilename = Tkinter.StringVar()
        self.queryFilename.set("1.csv")
        entryWidget = Tkinter.Entry(self.canvas, textvariable=self.queryFilename)
        entryWidget.grid(row=i,column=1,columnspan=2)
        
        sqlButton = tk.Button( self.canvas, text="Query", command=self.sqlQuery, width=10 )
        sqlButton.grid(row=i,column=0)
        i += 1
        
        #expand it to the size of the window and fill
        self.canvas.pack( expand=tk.YES, fill=tk.BOTH)
        return


    # build a frame and put controls in it
    def buildControls(self):

        # make a control frame
        self.cntlframe = tk.Frame(self.root)
        self.cntlframe.pack(side=tk.RIGHT, padx=2, pady=2, fill=tk.Y)

        # make a separator line
        sep = tk.Frame( self.root, height=self.initDy, width=2, bd=1, relief=tk.SUNKEN )
        sep.pack( side=tk.RIGHT, padx = 2, pady = 2, fill=tk.Y)

        # make a cmd 1 button in the frame
        self.buttons = []
        #width should be in characters. stored in a touple with the first one being a tag
        self.buttons.append( ( 'cmd1', tk.Button( self.cntlframe, text="Upload to db", command=self.uploaddb, width=10 ) ) )
        self.buttons[-1][1].pack(side=tk.TOP)  # default side is top
        
        return

    #Bind callbacks with the keyboard/keys
    def setBindings(self):
        #self.root.bind( '<Button-1>', self.handleButton1 )
        #self.root.bind( '<Button-2>', self.handleButton2 )
        #self.root.bind( '<Button-3>', self.handleButton3 )
        #self.root.bind( '<B1-Motion>', self.handleButton1Motion )
        self.root.bind( '<Command-q>', self.handleModQ )
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

    #set the rate on the MC2515
    def setRate(self,event=None):
        pass
    
    def sniff(self):
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
        self.comm.sniff(freq=self.freq,duration=time,
                  description=description,verbose=self.verbose,comment=comments,filename = None,
                   standardid=standardid, debug = False)    
        
    def uploaddb(self):
        print "Uploading all files"
        self.dm.uploadFiles()
        
    def sqlQuery(self):
        cmd = self.text.get(1.0,END)
        print cmd
        data = self.dm.getData(cmd)
        print data
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
        
        
# executes everything to run
if __name__ == "__main__":
    dapp = DisplayApp(650, 500, "ford_2004")
    dapp.main()