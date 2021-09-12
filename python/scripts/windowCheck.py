import sys
import os
import cv2
import numpy as np
sys.path.append(os.path.join(sys.path[0], '../'))

import RunescapeWindow

window = RunescapeWindow.RunescapeWindow()

while True:
    inventory = window.playAreaGet()
    stairs = ([50, 91, 139], [64, 105, 153])
    mask = cv2.inRange(inventory, np.array(stairs[0]), np.array(stairs[1]))
    cv2.imshow('inventory', mask)
    cv2.waitKey(1000)
