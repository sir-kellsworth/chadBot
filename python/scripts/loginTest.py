#!/usr/bin/python3

import sys
import os
sys.path.append(os.path.join(sys.path[0], '../'))
import Profile
import RunescapeWindow

profile = Profile.Profile("config/miner.py")
window = RunescapeWindow.RunescapeWindow()

window.worldPick()
window.login(profile.emailGet(), profile.passwordGet())
