#!/usr/bin/python3

import sys
import os
sys.path.append(os.path.join(sys.path[0], os.getcwd() + '/python'))
print(sys.path)

from bots.Miner import Miner
import Profile
import RunescapeWindow
import signal
import time

configFile = os.getcwd() + "/config/clayMiner.config"
profile = Profile.Profile(configFile)
window = RunescapeWindow.RunescapeWindow()

bot = Miner(profile, window, debug=True)

while True:
    bot.step()
print("finished mining")
