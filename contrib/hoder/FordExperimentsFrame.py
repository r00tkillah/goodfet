import Tkinter

tk = Tkinter


class FordExperimentsFrame:

    def __init__(self, frame, communicationLink):
        self.comm = communicationLink
        entryLabel = tk.Label(frame, text="Ford Focus 2004 -- High Speed CAN demonstrations", font = "Helvetica 16 bold italic")
        entryLabel.grid(row=i,column=0,columnspan=3,sticky=tk.W)
        
        i += 1
        entryLabel = tk.Label(frame, text="Set Speedometer:")
        entryLabel.grid(row=i,column=0,sticky=tk.W)
        self.speedVar = tk.StringVar()
        self.speedVar.set("")
        entryWidget = tk.Entry(frame, textvariable=self.speedVar)
        entryWidget.grid(row=i,column=1,sticky=tk.W)
        b = tk.Button(frame, command=self.setSpeedometer, text="Run")
        b.grid(row=i,column=2,sticky=tk.W)
        
        i += 1
        
        entryLabel = tk.Label(frame, text="Set RPMs:")
        entryLabel.grid(row=i,column=0,sticky=tk.W)
        self.rpmVar = tk.StringVar()
        self.rpmVar.set("")
        entryWidget = tk.Entry(frame, textvariable= self.rpmVar)
        entryWidget.grid(row=i,column=1,sticky=tk.W)
        b = tk.Button(frame, command=self.setRPM, text = "Run")
        b.grid(row=i,column=2,sticky=tk.W)
        
        i += 1
        
        entryLabel = tk.Label(frame, text="Set Temp:")
        entryLabel.grid(row=i,column=0, sticky=tk.W)
        self.engineTempVar = tk.StringVar()
        self.engineTempVar.set("")
        entryWidget = tk.Entry(frame, textvariable=self.engineTempVar)
        entryWidget.grid(row=i,column=1,sticky=tk.W)
        b = tk.Button(frame, command = self.setEngineTemp, text="Run")
        b.grid(row=i,column=2,sticky=tk.W)
    
    def setSpeedometer(self):
        try:
            setValue = int(self.speedVar.get())
        except:
            tkMessageBox.showwarning('Invalid input', \
                'Input is not an integer')
        self.comm.cycledb1_1056(10)
        
        #CALL METHOD
        
    def setRPM(self):
        try:
            rpmVal = int(self.rpmVar.get())
        except:
            tkMessageBox.showwarning('Invalid input', \
                'Input is not an integer')
        #CALL METHOD    
        
    def setRPM(self):
        try:
            engineTemp = int(self.engineTempVar.get())
        except:
            tkMessageBox.showwarning('Invalid input', \
                'Input is not an integer')
        #CALL METHOD    
        