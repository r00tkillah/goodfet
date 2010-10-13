import sys
import em260_data as em

##########################################
# Name: em260_spi_disass.py
# Author: Don C. Weber
# Usage: em260_spi_disass.py <file>
#
# Notes: This tool will parse SPI data from a Beagle
#        dump file taken while monitoring the EM250/EM260.
#        You can pass it either MOSI, MISO, 
#        or Bidirectional data.  This will output to
#        STDOUT.
##########################################

#debug = 0   # 0 == off, 1 == on
debug = 1   # 0 == off, 1 == on

def process_data(ascii_data):
    byte = 0

    while byte != len(ascii_data):
        outLine = []
        spi_byte = int(ascii_data[byte:byte+2],16)    # process this byte
        byte += 2       # next byte

        # ORDER IS IMPORTANT HERE SO LIMIT TABLE ASSOCIATED
        # WITH SPI BYTE VALUES
    
        # Continuation Test
        # Do this first to save on processing
        if spi_byte == 0xFF:
            #if debug: print ":	".join(outLine)
            continue
    
        # SPI Error Test
        # Do this second to save on processing
        if spi_byte <= 0x04:
            # Grab byte error
            #outLine.append("Error Byte")
            outLine.append(ascii_data[byte:byte+2])
            byte += 2       # next byte
            # Termination Test
            if int(ascii_data[byte:byte+2],16) != 0xA7:
                outLine.append("Frame Termination Error")
                outLine.append(ascii_data[byte:byte+2])
            print ":	".join(outLine)
            byte += 2       # next byte
            continue

        # SPI Version Response Test
        # Do this third to keep it from the truncated SPI table
        # FIXME: A mask should work here!!!
        #if ((spi_byte & em.spi_version_mask) == 0x80):
        if ((spi_byte >= 0x81) and (spi_byte <= 0xBF)):
            outLine.append("SPI Version")
            outLine.append(hex(spi_byte))
            # Termination Test
            if int(ascii_data[byte:byte+2],16) != 0xA7:
                outLine.append("Frame Termination Error")
                outLine.append(ascii_data[byte:byte+2])
            print ":	".join(outLine)
            byte += 2       # next byte
            continue

        # SPI Byte Value
        try:        # Test for value else error
            outLine.append(em.spi_values[em.spi_bytes.index(spi_byte)])
        except:
            outLine.append("Unknown SPI Byte Value")
            outLine.append(repr(hex(spi_byte)))
            print ":	".join(outLine)
            continue
    
        # SPI Protocol Version and Status Test
        if spi_byte in em.spi_pro_stat:
            # Termination Test
            if int(ascii_data[byte:byte+2],16) != 0xA7:
                outLine.append("Frame Termination Error")
                outLine.append(ascii_data[byte:byte+2])
            print ":	".join(outLine)
            byte += 2       # next byte
            continue
    
        # EZSP Frame Test
        # Process the Frame
        if spi_byte == 0xFE:
            # Get Frame Length
            data_length = int(ascii_data[byte:byte+2],16)
            data_length *= 2     # For ASCII the length must be doubled
            if debug: 
                outLine.append("Len")
                outLine.append(str(data_length))
            byte += 2       # next byte
    
            # Use Length to get Frame Data
            data_frame = ascii_data[byte:byte+data_length]
            if debug: 
                outLine.append("Data")
                outLine.append(str(data_length))
            byte += data_length       # skip frames
    
            # Test for Frame Terminator before processing
            if int(ascii_data[byte:byte+2],16) != 0xA7:
                outLine.append("Frame Termination Error")
                outLine.append(ascii_data[byte:byte+2])
                # Carrying on to next input
                print ":	".join(outLine)
                byte += 2       # next byte
                continue
    
            # Process Frame Data
            dfdata = 0
    
            # Handle Frame Counter
            outLine.insert(0, data_frame[dfdata:dfdata+2])
    
            # Handle Data
            dfdata += 2       # next byte
            cmd_data = int(data_frame[dfdata:dfdata+2],16)
    
            # Response Test
            if (cmd_data & em.cmd_mask):
                outLine.append("RESP")
                # Overflow Test
                if (cmd_data & em.resp_over_mask):
                    outLine.append(em.resp_overflow)
                # Truncated Data Test
                if (cmd_data & em.resp_trun_mask):
                    outLine.append(em.resp_truncated)
            # Command Test
            else:
                # Try in case reserved bits set take em.cmd_control out of range
                try:
                    outLine.append(em.cmd_control[cmd_data])
                except:
                    outLine.append("Unknown Control Command")
                    # Carrying on to next input
                    byte += 2       # next byte
                    continue
    
            # Frame Identification (A.K.A.: VERB)
            dfdata += 2       # next byte
            frame_id_data = int(data_frame[dfdata:dfdata+2],16)
            try:
                outLine.append(em.frame_ids[frame_id_data])
            except:
                outLine.append("Unknown Frame Id")
    
            # Frame Data
            # Not Implemented but we can tack it onto the end
            # for manual checking
            dfdata += 2       # next byte
            if dfdata < len(data_frame):
                outLine.append("Frame Data")
                outLine.append(data_frame[dfdata:])
    
            # Carrying on to next input
            print outLine
            print ":	".join(outLine)
            byte += 2       # next byte
            continue

#################
# Main
#################

# Get Input - Remove whitespaces just in case
#ascii_data = sys.argv[1].replace(' ','')
if __name__ == "__main__":
        INF = open(sys.argv[1],'r')

        for line in INF.readlines():
            indata = line.replace(' ','').strip()
            process_data(indata)
