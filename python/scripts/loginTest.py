#!/usr/bin/python3

import sys
import os
sys.path.append(os.path.join(sys.path[0], '../'))
import RunescapeWindow

window = RunescapeWindow.RunescapeWindow()

window.worldPick()
window.login("chadsbutt@gmail.com", "McDemShoulders")
