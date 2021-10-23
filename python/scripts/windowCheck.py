#!/usr/bin/python3

import sys
import os
import cv2
import numpy as np
sys.path.append(os.path.join(sys.path[0], os.getcwd() + '/python'))

import RunescapeWindow

window = RunescapeWindow.RunescapeWindow()

while True:
    inventory = window.playAreaGet()
    stairs = ([2, 49, 71], [6, 53, 75])
    mask = cv2.inRange(inventory, np.array(stairs[0]), np.array(stairs[1]))
    cv2.imshow('actual', inventory)
    cv2.imshow('mask', mask)
    cv2.waitKey(200)
