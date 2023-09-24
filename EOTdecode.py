#!/usr/bin/python3

import sys
import time
import subprocess
import sys
import datetime
import collections
import signal
import traceback
import json
from eot_decoder import EOT_decode, dumpEOT, printEOT
import EOTconfig


"""

This script pipes together a bunch of tools to decode End-Of-Train transmissions
    - RTL_FM (SDR) as a source (can be configured in EOTconfig)
    - SoX to re-sample the output from RTL_FM (signed, 16 bit integer) and convert to float (required by MiniModem)
    - MiniModem to decode the baseband FSK and output raw binary strings to this script
    
    * Note - Minimodem does not inherently take input from stdin; a special build of minimodem is required
           - See install.sh for the specific git repo 

"""
    
def signal_handler(sig, frame):
    global RUNNING
    RUNNING = 0


def main():

    '''    
    Verify it is a "1" or "0" from minimodem stdout by trying to convert it to and integer
    This will continue the loop and ignore any characters that don't meet this criteria
    Unfortunately we can't tailor the output of minimodem, so we work with strings
    This is mainly to deal with newlines minimodem spits out
    '''

    while RUNNING:

        #data = sys.stdin.read(1)
        data = minimodem_proc.stdout.read(1).decode()
        try:
            test = int(data)
        except ValueError:
            continue
            
        #print(data)
        queue.append(data)                     # append each new symbol to deque
        buffer = ''                                 # clear buffer

        for bit in queue:                           # move deque contents into buffer
            buffer += bit

        if (buffer.find('10101011100010010') == 0): # look for frame sync
            EOT = EOT_decode(buffer[6:])            # first 6 bits are bit sync
            if (EOT.valid):
                printEOT(EOT)
                dumpEOT(EOT)



RUNNING = 1
signal.signal(signal.SIGINT, signal_handler)

rtl_proc = None
sox_proc = None
minimodem_proc = None

rtl_cmd = ['rtl_fm', '-M', 'fm', '-f', str(EOTconfig.FREQ), '-s', '48000', '-p', str(EOTconfig.PPM), '-d', str(EOTconfig.DEVICE)]

if EOTconfig.GAIN:
    rtl_cmd.append('-g')
    rtl_cmd.append(str(EOTconfig.GAIN))
    
sox_cmd = ['sox', '-t', 'raw', '-esigned-integer', '-b', '16', '-r', '48000', '-', '-efloating-point', '-r', '48000', '-t', 'raw', '-']
modem_cmd = ['minimodem', '-M', '1200', '-S', '1800', '--binary-raw', '8', '1200', '-O', '-q']


'''
Initialize all of the processes and pipe them together
If using SDR - fire up RLT_FM and SoX, otherwise start minimodem without a piped input (will use audio default input)
'''

if EOTconfig.USE_RTL:
    print('====== Using RTL SDR as input source - Starting rtl_fm...\n', file=sys.stderr)
    rtl_proc = subprocess.Popen(rtl_cmd, stdout=subprocess.PIPE)
    print('====== Starting SoX...\n', file=sys.stderr)
    sox_proc = subprocess.Popen(sox_cmd, stdin=rtl_proc.stdout, stdout=subprocess.PIPE)
    print('====== Starting MiniModem with stdin input...\n', file=sys.stderr)
    minimodem_proc = subprocess.Popen(modem_cmd, stdin=sox_proc.stdout, stdout=subprocess.PIPE)
    
else:
    print('====== Using soundcard input source - Starting MiniModem...\n', file=sys.stderr)
    modem_cmd.remove('-O') #remove stdin flag
    minimodem_proc = subprocess.Popen(modem_cmd, stdin=sox_proc.stdout, stdout=subprocess.PIPE)

queue = collections.deque(maxlen=256)

time.sleep(1)

main()

print('====== Shutting down RTL_FM, SoX, and MiniModem\n', file=sys.stderr)

if rtl_proc:
    rtl_proc.kill()
    rtl_proc.wait()
    rtl_proc = None

if sox_proc:
    sox_proc.kill()
    sox_proc.wait()
    sox_proc = None

minimodem_proc.kill()
minimodem_proc.wait()
minimodem_proc = None
print('====== Done!\n', file=sys.stderr)
