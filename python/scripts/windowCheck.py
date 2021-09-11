import sys
import os
import cv2
sys.path.append(os.path.join(sys.path[0], '../'))

import RunescapeWindow

window = RunescapeWindow.RunescapeWindow()

while True:
    inventory = window.inventoryAreaGet()
    cv2.imshow('inventory', inventory)
    cv2.waitKey(1000)
