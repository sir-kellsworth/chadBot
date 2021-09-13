#!/usr/bin/python

import sys
import os
sys.path.append(os.path.join(sys.path[0], '../'))
import RunescapeWindow
from InputReplay.inputRecord import InputRecord

if len(sys.argv) != 2:
    print("usage python3 mouseRecord.py dataFile.dat")
    exit(1)

filename = sys.argv[1]
window = RunescapeWindow.RunescapeWindow()
capture = InputRecord(window)
print("press esc to start")
capture.escWait()
print("recording")
capture.captureStart()
print("press esc to stop")
capture.escWait()
capture.captureStop()

print("saving")
capture.save(filename)
