#!/usr/bin/python3

import sys
import os
import signal
import time
sys.path.append(os.path.join(sys.path[0], os.getcwd() + '/python'))

from bots.Fighter import Fighter
import Profile
import RunescapeWindow

running = True
def signalHandler(sig, frame):
    running = False

STATE_MINING = 0
STATE_BANK_RUN = 1
STATE_BANK_DEPOSIT = 2
STATE_MINE_RUN = 3

configFile = os.getcwd() + "/config/fighter.config"
profile = Profile.Profile(configFile)
window = RunescapeWindow.RunescapeWindow()
signal.signal(signal.SIGINT, signalHandler)

bot = Fighter(profile, window, debug=False)

while running:
    bot.step()

window.close()
