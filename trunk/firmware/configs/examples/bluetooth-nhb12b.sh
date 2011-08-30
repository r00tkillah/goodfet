# source this, then make as usual.


# This is for an NHB12B Next Hope Badge wired into an RN41 Bluetooth
# module.  The DCO calibration is mandatory, and this device's chip
# happens to use 0x8F9E.  Your chip will be different.

export CFLAGS="-DSTATICDCO=0x8F9E"
export config="monitor nrf spi"
export mcu="msp430x2618"
export platform="nhb12b"
