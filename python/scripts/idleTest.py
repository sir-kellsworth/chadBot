#!/usr/bin/python3

import sys
import os
sys.path.append(os.path.join(sys.path[0], '../'))
print(sys.path)

from Mouse.IdleMouse import IdleMouse
import Profile
import RunescapeWindow
import signal
import time

configFile = os.getcwd() + "/config/fighter.config"
profile = Profile.Profile(configFile)
window = RunescapeWindow.RunescapeWindow()

idleMouse = IdleMouse(window)
idleMouse.idleStart()
time.sleep(30)
idleMouse.idleStop()
time.sleep(5)
idleMouse.idleStart()
time.sleep(7)
