#!/usr/bin/python3

import sys
import os
import signal
import time
sys.path.append(os.path.join(sys.path[0], os.getcwd() + '/python'))

from bots.Miner import Miner
import Profile
import RunescapeWindow

def signalHandler(sig, frame):
    window.close()

configFile = os.getcwd() + "/config/clayMiner.config"
profile = Profile.Profile(configFile)
window = RunescapeWindow.RunescapeWindow()
signal.signal(signal.SIGINT, signalHandler)

bot = Miner(profile, window, debug=True)

while True:
    bot.step()

window.close()
