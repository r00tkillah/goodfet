
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


sys.path.insert(0,'/Users/chris/svn/goodfet/trunk/client/')
from GoodFETMCPCAN import GoodFETMCPCAN;
from intelhex import IntelHex;
from sniff import *

# create a shorthand object for Tkinter so we don't have to type it all the time
tk = Tkinter

# This is a simple display class for the GOODTHOPTER10 board. It currently allows you to
# set the rate, sniff, write and save what is sniffed in 3 different forms. Raw, parsed, pcap.
# one can also store a time stamp on when a stimulus is added. All data will be written into the 
# following path ../../contrib/hoder/data/
class DisplayApp:

    # init function
    def __init__(self, width, height):
        #configure information
        #Initialize FET and set baud rate
        self.client=GoodFETMCPCAN();
        self.client.serInit();
        self.client.MCPsetup();
        #initial rate, can be changed
        self.rate = float(125);
        self.client.MCPsetrate(self.rate)
        
        
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
        
        #save threading capabilities
        #this will be the event to stop data gathering
        self.stopSniff = threading.Event();
        self.stopSniff.clear()
        #hold the thread
        self.sniffThread = None;
        #this will tell us if we are sniffing
        self.sniff = False;
        
        
    
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
        self.rateChoice.set("125");
        self.rateMenu = tk.OptionMenu(self.canvas,self.rateChoice,"83.3","100","125","250","500","1000")
        self.rateMenu.grid(row=i,column=1)
        rateButton = tk.Button(self.canvas,text="Set Rate",command=self.setRate,width=10)
        rateButton.grid(row=i,column=2)
        i += 1
        
        # create options to set the filenames for the various text files saved from
        # the experimental run

        #filename variables
        self.fileVars = [];
        self.checkButtonVar = []
        labels = ["Raw data file:", "Parsed data file:", "Pcap File:","Stimulus file:"]
        initialValue = ["test.txt", "test2.txt", "test3.pcap","test4.txt"]
        for k in range(0,4):
            varI = IntVar()
            varI.set(1);
            c = Checkbutton(self.canvas, variable = varI)
            c.grid(row=i,column=0)
            self.checkButtonVar.append(varI)
            entryLabel = Tkinter.Label(self.canvas)
            entryLabel["text"] = labels[k]
            entryLabel.grid(row=i,column=1)
            var = Tkinter.StringVar();
            var.set(initialValue[k])
            entryWidget = Tkinter.Entry(self.canvas, textvariable=var)
            entryWidget.grid(row=i,column=2)
            entryWidget["width"] = 10
            self.fileVars.append(var)
            i+=1

        
        #this sets the stimulus textfile start/stop information
        # label before it
        entryLabel = Tkinter.Label(self.canvas)
        entryLabel["text"] = "Stimulus Input:"
        entryLabel.grid(row=i,column=0);
        
        #input stimulus type
        self.entryWidget = Tkinter.Entry(self.canvas)
        self.entryWidget["width"]  = 20
        
        self.entryWidget.grid(row=i,column=1)
        
        #add an entry button
        self.stimString = tk.StringVar();
        self.stimString.set("Stimulus Start")
        self.stimButton = tk.Button(self.canvas, textvariable=self.stimString ,command=self.handleStim,width=10)
        self.stimButton.grid(row=i,column=2)
        i += 1;
        
        
       
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

        #startbuttonString
        self.sniffString = tk.StringVar();
        self.sniffString.set("Start");

        # make a cmd 1 button in the frame
        self.buttons = []
        #width should be in characters. stored in a touple with the first one being a tag
        self.buttons.append( ( 'cmd1', tk.Button( self.cntlframe, textvariable=self.sniffString, command=self.handleCmdButton, width=10 ) ) )
        self.buttons[-1][1].pack(side=tk.TOP)  # default side is top
        self.buttons.append(  ( 'cmd2', tk.Button( self.cntlframe, text="Write",command=self.handleWriteButton, width = 10)))
        self.buttons[-1][1].pack(side=tk.TOP)
        self.buttons.append( ('cmd3', tk.Button(self.cntlframe, text="pcapSave",command=self.savepcap, width = 10)))
        self.buttons[-1][1].pack(side=tk.TOP)
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
        self.root.bind('<Return>',self.handleStim )
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

    # this method will start data collection
    def handleCmdButton(self):
        if(self.sniff == False):
            self.initializeList()
            #set the board to listen
            self.client.MCPreqstatListenOnly();
            #reset stop condition
            self.stopSniff.clear();
            #create thread
            self.sniffThread = sniff(self.stopSniff,self.LList,self.client)
            #start thread
            self.sniffThread.start()
            #reset button to now allow the user to stop threading
            self.sniff = True
            self.sniffString.set("Stop Sniff")
        else:
            self.stopSniffing()
    
    # This metthod intiializes the Linked List as well as clears all files
    # that are going to be written to during the sniffing process. this ensures
    # that the files are blank when sniffing begins. BE CAREFUL WITH THIS, there is no 
    # check
    def initializeList(self):
        self.filenames = []
        #get filenames
        i = 0;
        for item in self.fileVars:
            if( self.checkButtonVar[i].get() == 1):
                self.filenames.append("./data/" +item.get())
            else:
                self.filenames.append(None)
           	i  += 1
    
        #initialize linked list
        self.LList = LL(filenames = self.filenames, fileBooleans = self.checkButtonVar)
        
        #if we are writing a stimulus file
        if( self.checkButtonVar[-1].get() == 1 ):
            #initialize the stimulus timestamp doc
            writeFile = open(self.filenames[-1],'wb')
            writeFile.close()
        
    # stop the program from sniffing the bus
    def stopSniffing(self):
        if(self.sniff):
            #this ends the sniffing thread
            self.stopSniff.set()
            self.sniff = False;
            self.sniffString.set("Start")
        

    def savepcap(self):
        print "saving..."
        self.LList.writeToPcap()
    
    # This will clear our axes and erase all the data
    def handleCmdButton2(self):
        return
        

    def handleCmd1(self):
        print 'handling command 1'
        return

    def handleCmd2(self):
        print 'handling command 2'
        return
    
    def handleCmd3(self):
        print "handling command 3"
        return

    def handleButton1(self, event):
        print 'handle button 1: %d %d' % (event.x, event.y)
        self.baseClick = (event.x, event.y)

    def handleButton2(self, event):
        print 'handle button 2: %d %d' % (event.x, event.y)
        # create an object
        return

    def handleButton1Motion(self, event):
        print "button motion"


    # this method will open a second dialog box that will allow the user to write to the
    # GOODTHOPTER10. It will also make sure that the board is not sniffing at the same time
    # by first stopping the sniffing capabilities
    def handleWriteButton(self):
        self.stopSniffing();
        dialog = InfoBox(parent = self.root, client = self.client,title="Write to BUS",rate = self.rate)
        pass

    # this method is called when the user wants to record a stimulus injection time
    # a timestamp from python's time.time() is written to a csv file with the note the user input
    # NOTE: time.time() is not the mnost accurate method for recording a timestamp
    def handleStim(self,event=None):
        if(self.sniff):
            if( (self.checkButtonVar[-1].get() == 1)):
                data = []
                #get timestamp
                timeStmp = time.time()
                data.append(timeStmp)
                #we are currently injecting stimulus, or starting
                if( self.isStimulus):
                    self.stimString.set("Start Stimulus")
                    self.isStimulus = False
                    data.append('STOP')
                else:
                    self.stimString.set("End Stimulus")
                    self.isStimulus = True
                    data.append('START')
                data.append(self.entryWidget.get())
                self.writeRow(data,self.filenames[-1])
        else:
            print "Must be in sniffing mode to write"
    #set the rate on the MC2515
    def setRate(self,event=None):
        self.client.MCPsetrate(float(self.rateChoice.get()))
        self.rate = float(self.rateChoice.get())
        print "Rate reset to " + self.rateChoice.get()
        
    #run the method
    def main(self):
        print 'Entering main loop'
        #lets everything just sit and listen
        self.root.mainloop()
        
        
# executes everything to run
if __name__ == "__main__":
    dapp = DisplayApp(500, 200)
    dapp.main()