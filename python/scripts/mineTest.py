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

print('started mineTest')
configFile = os.getcwd() + "/config/clayMiner.config"
passwordFile = sys.argv[1]
profile = Profile.Profile(configFile, passwordFile)

window = RunescapeWindow.RunescapeWindow()
signal.signal(signal.SIGINT, signalHandler)

bot = Miner(profile, window, debug=False)

while running:
    bot.step()

window.close()
