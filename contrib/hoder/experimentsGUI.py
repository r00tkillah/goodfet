#import Tkinter
from Tkinter import *
import csv
import time
import sys;
import binascii;
import array;
import datetime
import os
import thread
from mainDisplay import *
import tkMessageBox


# create a shorthand object for Tkinter so we don't have to type it all the time
tk = Tkinter


class experimentsGUI(Toplevel):
    
    #constructor method
    def __init__(self, parent, dClass, comm, data = None, title = None):
        
        Toplevel.__init__(self, parent)
        self.transient(parent)
        #top = self.top = Toplevel(parent)
        self.BOLDFONT = "Helvetica 16 bold italic"
        if title:
            self.title(title)
        #set parent
        self.parent = parent
        #set Data
        self.data = data
        self.dClass = dClass
        self.comm = comm
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
        #Sweep all ids experiments
        j = 0
        entryLabel = Tkinter.Label(master, font = self.BOLDFONT)
        entryLabel["text"] = "Sweep Std IDs:"
        entryLabel.grid(row=i,column=j,columnspan=3, sticky = tk.W)
        
        i+=1
        j = 0
        entryLabel=Tkinter.Label(master)
        entryLabel["text"] = "Time (s):"
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j+=1
        self.sniffTime = Tkinter.StringVar();
        self.sniffTime.set("2")
        entryWidget = Tkinter.Entry(master, textvariable=self.sniffTime)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=j, sticky=tk.W)
        j+=1
        #align with lower exp
        j += 2
        entryLabel = Tkinter.Label(master)
        entryLabel["text"] = "From: "
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j+=1
        self.lowSweep = Tkinter.StringVar();
        self.lowSweep.set("0")
        entryWidget = Tkinter.Entry(master, textvariable=self.lowSweep)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        j+=1
        entryLabel = Tkinter.Label(master)
        entryLabel["text"] = "To "
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j+=1
        self.HighSweep = Tkinter.StringVar();
        self.HighSweep.set("4095")
        entryWidget = Tkinter.Entry(master, textvariable=self.HighSweep)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        j+= 1
        sweepButton = Button(master, text="Start", width=5, command=self.sweepID)
        sweepButton.grid(row=i, column=j,sticky=tk.W)
        
        i += 1
        j = 0
        entryLabel = Tkinter.Label(master, font = self.BOLDFONT)
        entryLabel["text"] = "RTR sweep response:"
        entryLabel.grid(row=i,column=j,columnspan=3, sticky = tk.W)
        
        i+=1
        j = 0 
        entryLabel=Tkinter.Label(master)
        entryLabel["text"] = "Time (s):"
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j += 1
        #self.sniffTime = Tkinter.StringVar();
        #self.sniffTime.set("20")
        entryWidget = Tkinter.Entry(master, textvariable=self.sniffTime)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=j, sticky=tk.W)
        j += 1
        entryLabel = Tkinter.Label(master, text = "Attempts: ")
        entryLabel.grid(row=i, column = j, sticky=tk.W)
        j += 1
        self.attempts = Tkinter.StringVar();
        self.attempts.set("1")
        entryWidget = Tkinter.Entry(master, textvariable = self.attempts)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        j += 1
        entryLabel = Tkinter.Label(master)
        entryLabel["text"] = "From: "
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j += 1
        #self.lowSweep = Tkinter.StringVar();
        #self.lowSweep.set("0")
        entryWidget = Tkinter.Entry(master, textvariable=self.lowSweep)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        j += 1
        entryLabel = Tkinter.Label(master)
        entryLabel["text"] = "To "
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j += 1
        #self.HighSweep = Tkinter.StringVar();
        #self.HighSweep.set("4095")
        entryWidget = Tkinter.Entry(master, textvariable=self.HighSweep)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        j += 1
        sweepButton = Button(master, text="Start", width=5, command=self.RTRsweepID)
        sweepButton.grid(row=i, column=j,sticky=tk.W)
        j += 1
        i+= 1
        
        j = 0
        
        entryLabel = Tkinter.Label(master, font = self.BOLDFONT)
        entryLabel["text"] = "Generation Fuzzing:"
        entryLabel.grid(row=i,column=j,columnspan=3, sticky = tk.W)
        j +=3
        startButton = Tkinter.Button(master,text="Start",width=5,command=self.GenerationFuzz)
        startButton.grid(row=i,column=j,sticky=tk.W)
        i+=1
        self.fuzzData = {}
        j = 0 
        entryLabel = Tkinter.Label(master)
        entryLabel["text"] = "sID: "
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j +=1
        sID = Tkinter.StringVar()
        sID.set("")
        self.fuzzData['sID'] = sID
        entryWidget = Tkinter.Entry(master, textvariable=sID)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        j += 1
        entryLabel = Tkinter.Label(master)
        entryLabel["text"] = "Period (ms): "
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j +=1
        period = Tkinter.StringVar()
        period.set("")
        self.fuzzData['period'] = period
        entryWidget = Tkinter.Entry(master, textvariable=period)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        j += 1
        
        entryLabel = Tkinter.Label(master)
        entryLabel["text"] = "Writes: "
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j +=1
        writesPerFuzz = Tkinter.StringVar()
        writesPerFuzz.set("")
        self.fuzzData['writesPerFuzz'] = writesPerFuzz
        entryWidget = Tkinter.Entry(master, textvariable=writesPerFuzz)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=j,sticky=tk.W)
     
        j += 1
        entryLabel = Tkinter.Label(master)
        entryLabel["text"] = "Fuzzes : "
        entryLabel.grid(row=i,column=j,sticky=tk.W)
        j +=1
        Fuzzes = Tkinter.StringVar()
        Fuzzes.set("")
        self.fuzzData['Fuzzes'] = Fuzzes
        entryWidget = Tkinter.Entry(master, textvariable=Fuzzes)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=j,sticky=tk.W)
        
        i+=1 
        j = 0
        for k in range(1,11,3):
            entryLabel = Tkinter.Label(master)
            entryLabel["text"] = "low"
            entryLabel.grid(row=i,column=k)
            entryLabel = Tkinter.Label(master)
            entryLabel["text"] = "high"
            entryLabel.grid(row=i,column=k+1)
        i += 1
        j = 0
        k = 0
        for j in range (0, 12, 3):
            entryLabel = Tkinter.Label(master)
            entryLabel["text"] = "db%d:" %k
            entryLabel.grid(row=i,column=j, sticky= tk.W)
            varTempLow = Tkinter.StringVar()
            #self.fuzzData['db%d'%(k)] = varTempLow
            varTempLow.set("")
            entryWidget = Tkinter.Entry(master, textvariable=varTempLow)
            entryWidget.grid(row=i,column=j+1, sticky=tk.W)
            entryWidget["width"] = 5
            varTempHigh = Tkinter.StringVar()
            self.fuzzData['db%d'%(k)] = [varTempLow, varTempHigh]
            entryWidget = Tkinter.Entry(master, textvariable = varTempHigh)
            entryWidget["width"] = 5
            entryWidget.grid(row=i,column=j+2,sticky=tk.W)
            k += 1
            print k
        
        for j in range(0,12,3):
            entryLabel = Tkinter.Label(master)
            entryLabel["text"] = "db%d:" %((k))
            entryLabel.grid(row=i+1,column=j, sticky= tk.W)
            varTempLow = Tkinter.StringVar()
            #self.fuzzData['db%d'%((k))] = varTemp
            varTempLow.set("")
            entryWidget = Tkinter.Entry(master, textvariable=varTempLow)
            entryWidget.grid(row=i+1,column=j+1, sticky=tk.W)
            entryWidget["width"] = 5
            varTempHigh = Tkinter.StringVar()
            self.fuzzData['db%d'%(k)] = [varTempLow, varTempHigh]
            entryWidget = Tkinter.Entry(master, textvariable = varTempHigh)
            entryWidget["width"] = 5
            entryWidget.grid(row=i+1,column=j+2,sticky=tk.W)
            k +=1
    
        i += 2
        j=0

    def GenerationFuzz(self):
        print "generation Fuzz"
        if( not self.dClass.checkComm()):
            return
        sID = int(self.fuzzData['sID'].get())
        period = int(self.fuzzData['period'].get())
        writesPerFuzz = int(self.fuzzData['writesPerFuzz'].get())
        Fuzzes = int(self.fuzzData['Fuzzes'].get())
        dbInfo = {}
        for i in range(0,8):
            idx = 'db%d'%i
            dbValues = self.fuzzData.get(idx)
            dbInfo[idx] = [int(dbValues[0].get()), int(dbValues[1].get())]
        self.comm.generationFuzzer(self.dClass.freq, sID,dbInfo, period, writesPerFuzz, Fuzzes)
        

    def RTRsweepID(self):
        print "Sweep across given IDs requesting packets"
        if( not self.dClass.checkComm()):
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
            print "Values are not integers. Please check inputs and try again."
            return
        self.dClass.setRunning()
        #thread.start_new_thread(self.comm.rtrSweep,(self.dClass.getRate(), lowI, highI, attemptsI, sT, verbose))
        self.comm.rtrSweep(self.dClass.getRate(), lowI, highI, attemptsI, sT, verbose)
        self.dClass.unsetRunning()
 
    def sweepID(self):
        if( not self.dClass.checkComm()):
            return
        sniffTime = self.sniffTime.get()
        low = self.lowSweep.get()
        high = self.HighSweep.get()
        try:
            sT = int(sniffTime)
            lowI = int(low)
            highI = int(high)
        except:
            print "Values are not integers. Please check inputs and try again."
            return
        if( highI < lowI  or sT <= 0):
            print "Incorrectly formated inputs! Please check that lower ID is less than higher ID"
        self.dClass.setRunning()
        thread.start_new_thread(self.comm.filterStdSweep, (self.dClass.getRate(), lowI, highI, sT ))
        self.dClass.unsetRunning()
        
    
    #This is the cancel / ok button
    def buttonbox(self):
        #add standard button box
        box = Frame(self)
        
        #ok button
        #w = Button(box, text="Apply", width = 10, command = self.ok, default=ACTIVE)
        #w.pack(side=LEFT,padx=5,pady=5)
        # cancel button
        w = Button(box,text="Cancel", width=10,command = self.ok)
        w.pack(side=LEFT,padx=5,pady=5)
        
        self.bind("<Return>",self.ok)
        self.bind("<Escape>",self.ok)
        
        box.pack()
        
    # ok button will first validate the choices (see validate method) and then exit the dialog
    # if everything is ok 
    def ok(self, event = None):
        
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
