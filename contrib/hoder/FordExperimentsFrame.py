import Tkinter

tk = Tkinter


class FordExperimentsFrame:
    """
        This class is a module for our car specific demonstrations of hacks. It is specific
        to our Ford taurus 2004. This will build our window on the GUI to display the hacks that
        can be run. 
        
        @type frame: Tkinter Canvas or Frame
        @param frame: This will be the canvas or frame on which this constructor will
                      build all of the capabilities of the car module. 
                      
        @type communicationLink: class file
        @param communicationLink: This is the class that the user set for the other part of the 
                                  car specific module. This is expected to be a subclass of the 
                                  experiments class. This will contain the experiment methods that
                                  this class will create GUI widgets to run.
    """

    def __init__(self, frame, communicationLink):
        """
        This constructor will create all the widgets for the display
        as well as set all the bindings for the various hacks that can be
        done.
        
        """
        i = 0
        self.comm = communicationLink
        entryLabel = tk.Label(frame, text="Ford Focus 2004 -- High Speed CAN demonstrations", font = "Helvetica 16 bold italic")
        entryLabel.grid(row=i,column=0,columnspan=5,sticky=tk.W)
        
        #######################
        ### SET SPEEDOMETER ###
        #######################
        
        i += 1
        entryLabel = tk.Label(frame, text="Set Speedometer:")
        entryLabel.grid(row=i,column=0,sticky=tk.W)
        self.speedVar = tk.StringVar()
        self.speedVar.set("")
        entryWidget = tk.Entry(frame, textvariable=self.speedVar,width=5)
        entryWidget.grid(row=i,column=1,sticky=tk.W)
        b = tk.Button(frame, command=self.setSpeedometer, text="Run")
        b.grid(row=i,column=2,sticky=tk.W)
        
        
        ##########################
        #### FAKE SPEEDOMETER ####
        ##########################
        i+= 1
        entryLabel = tk.Label(frame, text="Move Speedometer Up:")
        entryLabel.grid(row=i,column=0,sticky=tk.W)
        self.speedIncrementVar = tk.StringVar()
        self.speedIncrementVar.set("")
        entryWidget = tk.Entry(frame,textvariable=self.speedIncrementVar,width=5)
        entryWidget.grid(row=i,column=1,sticky=tk.W)
        b = tk.Button(frame, command=self.speedIncremement,text="Run")
        b.grid(row=i,column=2,sticky=tk.W)
        
        ###############
        ### SET RPM ###
        ###############
        i += 1
        
        entryLabel = tk.Label(frame, text="Set RPMs:")
        entryLabel.grid(row=i,column=0,sticky=tk.W)
        self.rpmVar = tk.StringVar()
        self.rpmVar.set("")
        entryWidget = tk.Entry(frame, textvariable= self.rpmVar, width=5)
        entryWidget.grid(row=i,column=1,sticky=tk.W)
        b = tk.Button(frame, command=self.setRPM, text = "Run")
        b.grid(row=i,column=2,sticky=tk.W)
        
        ##################
        #### FAKE RPM ####
        ##################
        entryLabel = tk.Label(frame, text="Fake RPM:")
        entryLabel.grid(row=i,column=0,sticky=tk.W)
        self.rpmVarIncrement = tk.StringVar()
        self.rpmVarIncrement.set("")
        entryWidget = tk.Entry(frame, textvariable=self.rpmVarIncrement, width=5)
        entryWidget.grid(row=i,column=1,sticky=tk.W)
        b = tk.Button(frame, command=self.rpmIncrement, text="Run")
        
   
        
        #######################
        ### SET TEMPERATURE ###
        #######################
        
        i += 1
        
        entryLabel = tk.Label(frame, text="Set Temp:")
        entryLabel.grid(row=i,column=0, sticky=tk.W)
        self.engineTempVar = tk.StringVar()
        self.engineTempVar.set("")
        entryWidget = tk.Entry(frame, textvariable=self.engineTempVar, width=5)
        entryWidget.grid(row=i,column=1,sticky=tk.W)
        b = tk.Button(frame, command = self.setEngineTemp, text="Run")
        b.grid(row=i,column=2,sticky=tk.W)
    
        #######################
        ### RUN UP ODOMETER ###
        #######################
        i += 1
        b = tk.Button(frame, command = self.runOdometer, text="Increment Odometer")
        b.grid(row=i,column=0,columnspan = 2,sticky=tk.W)
        
        ############################
        #### SET WARNING LIGHTS ####
        ############################
        i += 1
        self.breakLight = tk.IntVar()
        self.breakLight.set(0)
        ch = tk.Checkbutton(frame, text="Break Light",variable =self.breakLight)
        ch.grid(row=i,column=0,sticky=tk.W)
        
        self.batteryLight = tk.IntVar()
        self.batteryLight.set(0)
        ch = tk.Checkbutton(frame, text="Battery Light", variable=self.batteryLight)
        ch.grid(row=i,column=1,sticky=tk.W)
        
        i += 1
        self.engineLight = tk.IntVar()
        self.engineLight.set(0)
        ch = tk.Checkbutton(frame, text="Engine Light", variable=self.engineLight)
        ch.grid(row=i,column=0,sticky=tk.W)
        
        self.checkFuelCapLight = tk.IntVar()
        self.checkFuelCapLight.set(0)
        ch = tk.Checkbutton(frame, text="Fuel Cap Light", variable =self.checkFuelCapLight)
        ch.grid(row=i,column=1,sticky=tk.W)
        
        self.dashBoardErrors = tk.IntVar()
        self.dashBoardErrors.set(0)
        ch = tk.Checkbutton(frame, text="-- dashboard", variable=self.dashBoardErrors)
        ch.grid(row=i,column=2,sticky=tk.W)
        
        i += 1
        b = tk.Button(frame, command=self.warningLights,text="Warning Lights")
        b.grid(row=i,column=0,columnspan=2,sticky=tk.W)
        
        
        #########################
        #### OVERHEAT ENGINE ####
        #########################
        i +=1
        b = tk.Button(frame, command = self.overHeatEngine, text="Overheat Engine")
        b.grid(row=i,column=0,columnspan=2)
        
    
    def overHeatEngine(self):
        pass
        
    def warningLights(self):
        """
        This method will call the hack that sets the warning lights on the display   
        """
        pass
    def runOdometer(self):
        """
        This method will call the hack that runs the odometer up
        """
        self.comm.runOdometer()
        
    def setSpeedometer(self):
        """
        This method will call the hack that sets the speedometer
        """
        try:
            setValue = int(self.speedVar.get())
        except:
            tkMessageBox.showwarning('Invalid input', \
                'Input is not an integer')
        self.comm.setMPH(setValue)
        
        
    def speedIncremement(self):
       try:
            setValue = int(self.speedIncrementVar.get())
       except:
            tkMessageBox.showwarning('Invalid input', \
                'Input is not an integer')
       self.comm.speedometerHack([setValue])
        
         
        
        
        
    def setRPM(self):
        """
        This method will call the hack that sets the RPM
        """
        try:
            rpmVal = int(self.rpmVar.get())
        except:
            tkMessageBox.showwarning('Invalid input', \
                'Input is not an integer')
        #CALL METHOD 
        self.comm.setRPM(rpmVal)   
        
    def rpmIncrement(self):
        """
        This method will call the hack that sets the RPM
        """
        try:
            rpmVal = int(self.rpmVarIncrement.get())
        except:
            tkMessageBox.showwarning('Invalid input', \
                'Input is not an integer')
        #CALL METHOD 
        self.comm.rpmHack(rpmVal) 
        
    def setEngineTemp(self):
        """
        This method will call the hack that sets the engine temp
        """
        try:
            engineTemp = int(self.engineTempVar.get())
        except:
            tkMessageBox.showwarning('Invalid input', \
                'Input is not an integer')
        #CALL METHOD    
        return
