#!/usr/bin/python3

import sys
import os
sys.path.append(os.path.join(sys.path[0], os.getcwd() + '/python'))
import Profile
import RunescapeWindow

profile = Profile.Profile("config/miner.py")
window = RunescapeWindow.RunescapeWindow()

screen = window.screenGet()
existingUserButton = window.imageMatch(screen, window.templates['clickToPlayButton'])
print(existingUserButton)
