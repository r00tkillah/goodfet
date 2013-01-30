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


class experiments(Toplevel):
    
    #constructor method
    def __init__(self, parent, dClass, comm, data, title = None):
        
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
        #Sweep all ids experiments
        entryLabel = Tkinter.Label(master, font = "Helvetica 16 bold italic")
        entryLabel["text"] = "Sweep Std IDs:"
        entryLabel.grid(row=i,column=0,columnspan=3, sticky = tk.W)
        i+=1
        entryLabel=Tkinter.Label(master)
        entryLabel["text"] = "Time (s):"
        entryLabel.grid(row=i,column=0,sticky=tk.W)
        self.sniffTime = Tkinter.StringVar();
        self.sniffTime.set("20")
        entryWidget = Tkinter.Entry(master, textvariable=self.sniffTime)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=1, sticky=tk.W)

        entryLabel = Tkinter.Label(master)
        entryLabel["text"] = "From: "
        entryLabel.grid(row=i,column=2,sticky=tk.W)
        
        self.lowSweep = Tkinter.StringVar();
        self.lowSweep.set("0")
        entryWidget = Tkinter.Entry(master, textvariable=self.lowSweep)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=3,sticky=tk.W)
        
        entryLabel = Tkinter.Label(master)
        entryLabel["text"] = "To "
        entryLabel.grid(row=i,column=4,sticky=tk.W)
        
        self.HighSweep = Tkinter.StringVar();
        self.HighSweep.set("4095")
        entryWidget = Tkinter.Entry(master, textvariable=self.HighSweep)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=5,sticky=tk.W)

        sweepButton = Button(master, text="Start", width=5, command=self.sweepID)
        sweepButton.grid(row=i, column=6,sticky=tk.W)
        i += 1
        
        entryLabel = Tkinter.Label(master, font = "Helvetica 16 bold italic")
        entryLabel["text"] = "RTR sweep response:"
        entryLabel.grid(row=i,column=0,columnspan=3, sticky = tk.W)
        i+=1
        entryLabel=Tkinter.Label(master)
        entryLabel["text"] = "Time (s):"
        entryLabel.grid(row=i,column=0,sticky=tk.W)
        self.sniffTime = Tkinter.StringVar();
        self.sniffTime.set("20")
        entryWidget = Tkinter.Entry(master, textvariable=self.sniffTime)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=1, sticky=tk.W)

        entryLabel = Tkinter.Label(master)
        entryLabel["text"] = "From: "
        entryLabel.grid(row=i,column=2,sticky=tk.W)
        
        self.lowSweep = Tkinter.StringVar();
        self.lowSweep.set("0")
        entryWidget = Tkinter.Entry(master, textvariable=self.lowSweep)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=3,sticky=tk.W)
        
        entryLabel = Tkinter.Label(master)
        entryLabel["text"] = "To "
        entryLabel.grid(row=i,column=4,sticky=tk.W)
        
        self.HighSweep = Tkinter.StringVar();
        self.HighSweep.set("4095")
        entryWidget = Tkinter.Entry(master, textvariable=self.HighSweep)
        entryWidget["width"] = 5
        entryWidget.grid(row=i,column=5,sticky=tk.W)
        
        sweepButton = Button(master, text="Start", width=5, command=self.RTRsweepID)
        sweepButton.grid(row=i, column=6,sticky=tk.W)
        
        i+= 1
        
        
     
        
    def RTRsweepID(self):
        print "RTR sweep ID"
 
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
            print "Values are not integers"
            return
        if( highI < lowI  or sT <= 0):
            print "Incorrectly formated inputs!"
        self.dClass.setRunning()
        thread.start_new_thread(self.comm.filterStdSweep, (self.freq, low, high, time ))
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