
# Chris Hoder
# 11/3/2012


#this is a simple linked list
class LL:
    #constructor
    def __init__(self,filenames,fileBooleans):
        #save filenames and booleans to know if we are writing that file
        self.filenames = filenames
        self.fileBooleans = fileBooleans
       
        #create/overwrite file only if we are 
        #saving that type of file
        for i in range(len(fileBooleans)):
            if( fileBooleans[i].get() == 1):
            	if(filenames[i] == None):
            		continue
                writeFile = open(filenames[i],'wb')
                writeFile.close()
        self.first = None
        self.last = None
        
    def addNode(self,node):
        for i in range(len(self.fileBooleans)):
            if( self.fileBooleans[i].get() == 1):
            	if( self.filenames[i] == None):
            		continue
                if( i == 0):
                    node.writeToFile(self.filenames[i])
                elif( i == 1):
                    node.writeParsed(self.filenames[i])
                elif( i == 2):
                    node.writePcap(self.filenames[i])

        #add the node to the linked list
        #check the initial condition edge case
        if( self.first == None):
            self.first = node
            self.last = node
        else:
            self.last.setNext(node)
            self.last = node
            
    