#!/usr/bin/env python3

"""
This is a library for Raspberry Pi to control Seeed Grove Air530 GPS module over serial
It most likely will not work
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

def startGPS(hot=False, reset = False) -> None:
    # Command 030 [hot/warm/cold], [system restart]
    # Start the GPS either hot or cold
    if type(hot) is bool and type(reset) is bool:
        pass
    else:
        raise Exception("Values for hot and reset must be in bool format")

    if hot:
        # hot start
        ser.write(createCommand("030,1,1*2C"))
    elif reset:
        # cold start
        ser.write(createCommand("030,3,1*2E"))
    else:
        # warm start
        ser.write(createCommand("030,2,1*2F"))

def setPositionMode(gps = True, glonass = False, beidou = False, galileo = False) -> None:
    # Command 115 [gps], [glonass], [beidou], [galileo]
    # Set what kind of positioning the module uses
    if type(gps) is bool and type(glonass) is bool and type(beidou) is bool and type(galileo) is bool:
        pass
    else:
        raise Exception("Values for GPS, glonass, beidou and galileo must be in bool format")

    if gps is False and glonass is False and beidou is False and galileo is False:
        raise Exception("You need to choose at least one positioning system")
    
    ser.write(createCommand(f'115,{int(gps)},{int(glonass)},{int(beidou)},{int(galileo)}*2B'))

def eraseAuxPositioning() -> None:
    # Command 040
    # Erase auxiliary positioning data in flash
    ser.write(createCommand("040*2B"))

def setNMEAoutputInterval(ms: int) -> None:
    # Command 101
    # Configure the interval for outputting NMEA messages (in milliseconds)
    if type(ms) is not int:
        raise Exception("Function accepts only int values")
    
    if ms in range(200,10001):
        ser.write(createCommand("101,{ms}*02"))
    else:
        raise Exception("The value must be between 200 and 10000")
    
def gotoStandby(stop = False) -> None:
    # Command 051
    # Enter standby low power mode
    
    if type(stop) is bool:
        pass
    else:
        raise Exception("Argument stop must be in bool format")
    
    if stop:
        # Stop mode
        ser.write(createCommand("051,0*36"))
    else:
        # Sleep mode
        ser.write(createCommand("051,1*36"))
