import Tkinter

tk = Tkinter


class FordExperimentsFrame:

    def __init__(self, frame, communicationLink):
        self.comm = communicationLink
        entryLabel = tk.Label(frame, text="test")
        entryLabel.grid(row=0,column=0)
        
        b = tk.Button(frame, command=self.testMETHOD, text="test")
        b.grid(row=0,column=1)
        
    
    def testMETHOD(self):
        print "test"