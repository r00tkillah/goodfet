##################################
## These are production boards.
##################################

#Unset by default, but can be explicitly overwritten.
config ?= undef


ifneq (,$(findstring $(board),goodfet40 goodfet41 goodfet42))
config=-D l=20 -D w=49 -D h=6 -D cutribbonslit=1
endif

ifneq (,$(findstring $(board),facedancer10 facedancer11))
config=-D l=23.5 -D w=71 -D h=6 -D cutsecondusb=1
endif

#The CONFIG_foo vars are only interpreted if $(config) is "unset".
ifeq ($(config),undef)
echo "Please set define board to your PCB style."
false
endif
