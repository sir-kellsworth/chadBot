#!/usr/bin/python

import sys
import os
sys.path.append(os.path.join(sys.path[0], '../'))
import RunescapeWindow

if len(sys.argv) != 2:
    print("usage python3 mouseRecord.py dataFile.dat")
    exit(1)

filename = sys.argv[1]
window = RunescapeWindow()
capture = InputRecord(window)
input("press esc to start")
capture.escWait()
capture.captureStart()
print("press esc to stop")
capture.escWait()
capture.captureStop()

print("saving")
capture.save(filename)
