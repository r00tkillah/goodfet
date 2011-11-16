mcu = undef
ifneq (,$(findstring $(board),goodfet20))
mcu := msp430x1612
endif

ifneq (,$(findstring $(board),goodfet30 goodfet31))
mcu := msp430x2274
endif

ifneq (,$(findstring $(board),goodfet40 goodfet41))
mcu := msp430x2618
endif

ifneq (,$(findstring $(board),goodfet50 goodfet51))
mcu := msp430x5510
endif

ifeq ($(mcu),undef)
$(error Please define board, as explained in the README)
endif

AVAILABLE_APPS = monitor spi jtag sbw jtag430 jtag430x2 i2c jtagarm7 ejtag jtagxscale openocd chipcon avr pic adc nrf ccspi glitch smartcard ps2 

CONFIG_sbw         = y

# defaults
CONFIG_monitor    ?= y
CONFIG_spi        ?= y
CONFIG_jtag       ?= n
CONFIG_sbw        ?= n
CONFIG_jtag430    ?= y
CONFIG_jtag430x2  ?= y
CONFIG_i2c        ?= n
CONFIG_jtagarm7   ?= n
CONFIG_ejtag      ?= n
CONFIG_jtagxscale ?= n
CONFIG_openocd    ?= y
CONFIG_chipcon    ?= y
CONFIG_avr        ?= y
CONFIG_pic        ?= n
CONFIG_adc        ?= n
CONFIG_nrf        ?= n
CONFIG_ccspi      ?= y
CONFIG_glitch     ?= n
CONFIG_smartcard  ?= n
CONFIG_ps2        ?= n


config := $(foreach app,$(AVAILABLE_APPS),$(if $(findstring $(CONFIG_$(app)),y yes t true Y YES T TRUE),$(app)))

