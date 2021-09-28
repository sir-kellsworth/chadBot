#!/usr/bin/python3

import numpy as np
import cv2
from PIL import ImageGrab
from pynput import mouse, keyboard
import time

#**************************************************************************
def snapshotGet():
    img = np.array(ImageGrab.grab())
    return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

#**************************************************************************
def colorShow(color):
    sample = np.zeros((300, 300, 3), np.uint8)
    sample[:] = color
    cv2.imshow('smaple', sample)
    cv2.waitKey(30)

#**************************************************************************
def onMove(x, y):
    color = screen[y][x]
    colorShow(color)
    print("color: " + str(color))

mouseListener = mouse.Listener(
    on_move=onMove,
    on_click=None,
    on_scroll=None
)

screen = snapshotGet()
mouseListener.start()
while True:
    time.sleep(0.5)
    screen = snapshotGet()

mouseListener.stop()
