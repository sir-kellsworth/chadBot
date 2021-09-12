#!/usr/bin/python

import sys
import os
sys.path.append(os.path.join(sys.path[0], '../'))
print(sys.path)

from bots.Miner import Miner
import Profile
import RunescapeWindow
import signal
import sys
import time

STATE_MINING = 0
STATE_BANK_RUN = 1
STATE_BANK_DEPOSIT = 2
STATE_MINE_RUN = 3

configFile = os.getcwd() + "/config/miner.config"
profile = Profile.Profile(configFile)
window = RunescapeWindow.RunescapeWindow()

bot = Miner(profile, window, debug=True)

while True:
    bot.step()
print("finished mining")