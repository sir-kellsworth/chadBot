#!/usr/bin/python3

import sys
import os
import signal
sys.path.append(os.path.join(sys.path[0], os.getcwd() + '/python'))
import Profile
import RunescapeWindow

def signalHandler(sig, frame):
    window.close()

if len(sys.argv) < 2:
    print("./loginTest.py passwordFile")
    exit(1)

passwordFile = sys.argv[1]
profile = Profile.Profile("config/miner.config", passwordFile)
window = RunescapeWindow.RunescapeWindow()
signal.signal(signal.SIGINT, signalHandler)

window.worldPick()
window.login(profile.emailGet(), profile.passwordGet())

window.close()
