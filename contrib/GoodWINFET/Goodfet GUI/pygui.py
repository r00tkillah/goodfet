#!/usr/bin/env python
#Riley Porter
#Rileyporter @ gmail .com
#This was 1 hour of lame pygtk skills.

import sys
import time
import random 

try:
	import pygtk
	pygtk.require("2.0")
except:
	pass
	
try:
	import gtk
	import gtk.glade
except:
	print "Failed to load needed gtk libs"
	sys.exit(1)


class GUI:
	def __init__(self):
		
		self.firmware = ""
		self.gladefile = "pygui.glade"
		self.wTree = gtk.glade.XML("pygui.glade")
		self.window = self.wTree.get_widget("MainWindow")
		self.window.set_title("Goodfet GUI Programmer")
		self.button_Program = self.wTree.get_widget("btnProgram")
		self.button_Open = self.wTree.get_widget("btnOpen")
		self.statusbar = self.wTree.get_widget("statusbar")
		self.fileEntry = self.wTree.get_widget("fileEntry")
		self.statusText = self.wTree.get_widget("statusText")
		self.wTree.signal_autoconnect(self)
		
		#Text Buffer Initialize Code
		self.textBuffer = gtk.TextBuffer()
		self.textBuffer.set_text("Feed the fet")
		self.statusText.set_buffer(self.textBuffer)

		
	###BUTTON FUNCTIONS HERE###
	
	def on_btnProgram_clicked(self, widget):
		"""Program the goodfet function here"""
		if self.firmware == "":
			print "[*] Please select a firmware image"
			###Run this if program was placed before a firmware image was selected###			
			self.statusbar.push(0,"Please select a firmware image")
		else:
			print "[*] Programming Please Wait...."
			"""This is where you would place the programming code"""
			self.dummyText(widget) 
			
	
	def on_btnVerify_clicked(self, widget):
		"""Add Verify Code Calls Here"""
		print "[*] Verifying...."
	
	def on_btnErase_clicked(self, widget):
		"""Add Erase Calls Here"""
		print "[*] Erasing.... "
			
	def on_btnOpen_clicked(self,widget):
		print "[*]Opening File Chooser"
		dialog = gtk.FileChooserDialog("Open...",None, gtk.FILE_CHOOSER_ACTION_OPEN,(gtk.STOCK_CANCEL,
		                                                                             gtk.RESPONSE_CANCEL,
		                                                                             gtk.STOCK_OPEN,
		                                                                             gtk.RESPONSE_OK))
		#Selected Firmware image code
		response = dialog.run()
		if response == gtk.RESPONSE_OK:
			selectedFile = dialog.get_filename()
			self.firmware = selectedFile
			#self.fileEntry = gtk.Entry()
			self.fileEntry.set_text(selectedFile)
			print "[*] File Selected: " + selectedFile #Debug Info
			self.statusbar.push(0,"") #Clears the error text in the status bar
			dialog.destroy()
		
		elif response == gtk.RESPONSE_CANCEL:
			print "[*] No File Selected"
			dialog.destroy()
			
	###BUTTON FUNCTIONS ENDED###
			
	def on_quitActivate(self, widget):
		"""Tie quit Signal from mainwindow to exit"""
		gtk.main_quit()
	
	def dummyText(self, widget):
		"""Dummy program to create data for the textbuffer code"""
		x = 0
		while x != 20:
			x = x+1
			print random.randint(0,203250)
			#self.textBuffer.set_text(str(random.randint(0,203250)))
			#self.statusText.set_buffer(self.textBuffer)
			#This is ugly as shit.  But F me if I cant remember how to scroll text buffers..
			#self.statusText.get_buffer()
			self.textBuffer = self.statusText.get_buffer()
			self.textBuffer.insert(self.textBuffer.get_end_iter(),str(random.randint(0,203250)))
			#self.statusText.scroll_to_iter(buf.get_end_iter(),0)
			time.sleep(.1)	
		
if __name__ == "__main__":
	print "[*]Goodfet Programmer Started..."
	run = GUI()
	gtk.main()
    
