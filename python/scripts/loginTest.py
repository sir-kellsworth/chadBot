#!/usr/bin/python3

import sys
import os
import signal
sys.path.append(os.path.join(sys.path[0], os.getcwd() + '/python'))
import Profile
import Window.RunescapeWindow

def signalHandler(sig, frame):
    window.close()

profile = Profile.Profile("config/miner.py")
window = RunescapeWindow.RunescapeWindow()
signal.signal(signal.SIGINT, signalHandler)

window.worldPick()
window.login(profile.emailGet(), profile.passwordGet())

window.close()
