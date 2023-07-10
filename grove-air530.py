#!/usr/bin/env python3

"""
This is a library for Raspberry Pi to control Seeed Grove Air530 GPS module over serial
It most likely will not work. 

The source is this wonderful document: 

https://files.seeedstudio.com/wiki/Grove-GPS_Air_530/Air530_GPS_User_Booklet.V1.7.pdf

... which is in Chinese. I don't understand Chinese, so I used google translate on it and thus
this library is based on a google translated Chinese PDF, by a guy that is not a professional
python coder.

You have been warned.

This library access the Air350 by using the GKC interface data format.

The structure of the GKC interface is:
[$PGKC][Command][Arguments][*][Checksum][<CR>][<LF>]

(c) Joonas Joensuu, 2023

"""

import serial

ser = serial.Serial("/dev/ttyS0", 9600)

def createCommand(gpscmd: str) -> bytes:
    """
    Basically creates the UART-query for transmitting

    command must be in format eg. 010,1,1*2S,
    where the first 3 digits represent the command and the
    following arguments are arguments sent to the command
    and end should be a checksum
    """

    if type(gpscmd) is str:
        pass
    else:
        raise Exception("Function takes only strings as arguments")


    # Test validity of entered command
    parts = gpscmd.split(",")
    cmd = parts[0]

    # first see if the command is in a three-digit integer format
    try:
        if len(cmd) != 3:
            raise Exception("Command should be a 3-digit integer")
        try:
            cmdInt = int(cmd)
        except:
            raise Exception("Command should be a 3-digit integer")
        
    # Then check the validity of the checksum
    cs_split = gpscmd.split("*")
    cs = cs_split[-1]
    hexchars = set("0","1","2","3","4","5","6","7","8","9","A","B","C","D","E","F")
    if len(cs) != 2:
        raise Exception("Checksum must be a hex value between 00-FF")
    elif cs[0] not in hexchars:
        raise Exception("Checksum must be a hex value between 00-FF")
    elif cs[1] not in hexchars:
        raise Exception("Checksum must be a hex value between 00-FF")
    else:
        pass
    
    # And finally check if each argument separated by a comma is an integer
    if len(parts) > 1: # a command can be entered without arguments - if so, skip this part
        args = parts[1:]
        last_argument_with_checksum = args[-1]
        last_argument = last_argument_with_checksum.split("*")[0]
        args[-1] = last_argument # remove the checksum for testing to proceed
        for arg in args:
            try:
                test = int(arg)
            except:
                raise Exception("Arguments must be integers!")
        
    # So if the command passed all the tests for validity, create the complete command

    msg = f'$PGKC{gpscmd}<CR><LF>'
    result = bytes(msg, 'utf-8')
    return result

def transmit(cmd: bytes) -> None:
    # The final function that actually passes the arguments to the GPS module
    # If used on a microcontroller instead of a Raspberry Pi, then that may need
    # another function for transmitting

    if type(cmd) is not bytes:
        raise Exception("Transmitted command must be of type bytes")
    ser.write(cmd)

def startGPS(hot=False, reset = False) -> bytes:
    # Command 030 [hot/warm/cold], [system restart]
    # Start the GPS either hot or cold
    if type(hot) is bool and type(reset) is bool:
        pass
    else:
        raise Exception("Values for hot and reset must be in bool format")

    if hot:
        # hot start
        return createCommand("030,1,1*2C")
    elif reset:
        # cold start
        return createCommand("030,3,1*2E")
    else:
        # warm start
        return createCommand("030,2,1*2F")

def setPositionMode(gps = True, glonass = False, beidou = False, galileo = False) -> bytes:
    # Command 115 [gps], [glonass], [beidou], [galileo]
    # Set what kind of positioning the module uses
    if type(gps) is bool and type(glonass) is bool and type(beidou) is bool and type(galileo) is bool:
        pass
    else:
        raise Exception("Values for GPS, glonass, beidou and galileo must be in bool format")

    if gps is False and glonass is False and beidou is False and galileo is False:
        raise Exception("You need to choose at least one positioning system")
    
    return createCommand(f'115,{int(gps)},{int(glonass)},{int(beidou)},{int(galileo)}*2B')

def eraseAuxPositioning() -> bytes:
    # Command 040
    # Erase auxiliary positioning data in flash
    return createCommand("040*2B")

def setNMEAoutputInterval(ms: int) -> bytes:
    # Command 101
    # Configure the interval for outputting NMEA messages (in milliseconds)
    if type(ms) is not int:
        raise Exception("Function accepts only int values")
    
    if ms in range(200,10001):
        return createCommand("101,{ms}*02")
    else:
        raise Exception("The value must be between 200 and 10000")
    
def gotoStandby(stop = False) -> bytes:
    # Command 051
    # Enter standby low power mode
    
    if type(stop) is bool:
        pass
    else:
        raise Exception("Argument stop must be in bool format")
    
    if stop:
        # Stop mode
        return createCommand("051,0*36")
    else:
        # Sleep mode
        return createCommand("051,1*36")

# TODO: 105 - Enter Periodic Low Power Mode
# TODO: 113 - Enable or disable QZSS NMEA format output
# TODO: 114 - Turn on or off the QZSS function
# TODO: 115 - Set star search mode
# TODO: 147 - Set NMEA output baud rate
# TODO: 149 - Set NMEA serial port parameters
# TODO: 161 - PPS settings
# TODO: 201 - Interval for querying NMEA messages
# TODO: 202 - Interval at which NMEA messages are returned (response to 201 command)
# TODO: 239 - Turn on or off the SBAS function
# TODO: 240 - Query whether SBAS is enabled
# TODO: 241 - Return whether SBAS is enabled (response to 240 command)
# TODO: 242 - Set NMEA sentence output enable
# TODO: 243 - Query the output frequency of NMEA sentences
# TODO: 244 - Returns NMEA sentence output frequency (response to 243 command)
# TODO: 278 - Set RTC time
# TODO: 279 - Query RTC time
# TODO: 280 - Returns NMEA sentence output frequency (response to 243 command)
# TODO: 284 - Set the speed threshold, when the speed is lower than the threshold value, the output speed is 0
# TODO: 350 - Set the HDOP threshold, when the actual HDOP is greater than the threshold, no positioning
# TODO: 357 - Get HDOP Threshold
# TODO: 462 - Query the version number of the current software
# TODO: 463 - Returns the version number of the current software (response to the 462 command)
# TODO: 630 - Set approximate location information and time information to speed up positioning
