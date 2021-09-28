import sys
import os
import cv2
import numpy as np
sys.path.append(os.path.join(sys.path[0], '../'))

import RunescapeWindow

window = RunescapeWindow.RunescapeWindow()

while True:
    inventory = window.playAreaGet()
    stairs = ([99, 112, 122], [111, 150, 140])
    mask = cv2.inRange(inventory, np.array(stairs[0]), np.array(stairs[1]))
    cv2.imshow('actual', inventory)
    cv2.imshow('mask', mask)
    cv2.waitKey(200)
