#!/usr/bin/python3

import sys
import os
import signal
import time
sys.path.append(os.path.join(sys.path[0], os.getcwd() + '/python'))

from bots.Miner import Miner
import Profile
import RunescapeWindow

running = True
def signalHandler(sig, frame):
    global running
    print('caught signal')
    running = False

configFile = os.getcwd() + "/config/clayMiner.config"
profile = Profile.Profile(configFile)
window = RunescapeWindow.RunescapeWindow()
signal.signal(signal.SIGINT, signalHandler)

bot = Miner(profile, window, debug=False)

while running:
    bot.step()

print("bot done")
window.close()
