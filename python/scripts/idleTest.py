#!/usr/bin/python3

import sys
import os
import signal
import time
sys.path.append(os.path.join(sys.path[0], os.getcwd() + '/python'))

from Mouse.IdleMouse import IdleMouse
import Profile
import RunescapeWindow

def signalHandler(sig, frame):
    window.close()

configFile = os.getcwd() + "/config/fighter.config"
profile = Profile.Profile(configFile)
window = RunescapeWindow.RunescapeWindow()
signal.signal(signal.SIGINT, signalHandler)

idleMouse = IdleMouse(window)
idleMouse.idleStart()
time.sleep(30)
idleMouse.idleStop()
time.sleep(5)
idleMouse.idleStart()
time.sleep(7)
