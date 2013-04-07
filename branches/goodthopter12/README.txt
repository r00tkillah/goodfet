GoodThopter12 CAN Adapter


IMPORTANT - "PLUG BUG FIX"

It turns out OBD2 cables have a variety of pinouts, specifically at
the DB9 connector. The two most popular for CAN that I have seen are
CANH on pins (7,3) and CANL on (5,2) - to accommodate both pinouts
GoodThopter12 includes resistors (R5-R8) that are 0 OHM and act as
jumpers to connect the pins that correlate to your cable.

EX: The Sparkfun cable supports CANH on pin 3 and CANL on pin 5 so you
would connect resistors R7 and R6 to support your cable.

--

The GoodThopter is the sexy GoodFET CAN Adapter, whose purpose is to
route CAN connection from an automobile or ECU into a laptop
leveraging the maturing GoodFET firmware and project.  Care has been
taken to keep the design easy to solder and the code easy to modify.

If you like this project, the following will humbly accept beer
donations:

Andrew Righter, GoodThopter Project Lead
Travis Goodspeed, Circuit Preacher

CAN Hacking Inspired By:
-Late night drinking in the Midwest with Atlas and Cutaway.
-Late night drinking in Downtown Metropolitan Etna with Sergey Bratus
 singing ``Hop on the Magic School Bus!''
-Late night cramming in Philly to meet an absurd deadline that's
 demonstrably Andrew's fault, but without which you wouldn't have a
 neighborly GoodThopter.

If you have any questions/comments:

Andrew Righter <andrew@215LAB.com>

bugs/development:
http://goodfet.sf.net/
goodfet-devel@lists.sourceforge.net
