#For Mac, install the following.
# XCode
# MacPorts
# FTDI Virtual COM Driver

# In Linux, the FTDI driver should be included by default.  Be sure
# that the user is allowed to use /dev/ttyUSB0, which often requires
# being a member of the dialout group.

# Now install these packages.  They might have different names.
# python-serial wget subversion gcc-msp430 curl

# Use subversion to grab the code.
mkdir -p ~/svn; cd ~/svn
svn co https://goodfet.svn.sourceforge.net/svnroot/goodfet

# Then link the client into /usr/local/bin/
# You could also add the client directory to your $PATH.
cd ~/svn/goodfet/trunk/client
sudo make link

# Load firmware, not yet building it locally.
goodfet.bsl --fromweb
goodfet.monitor test


