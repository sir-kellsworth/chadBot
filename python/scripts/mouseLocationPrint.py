#!/usr/bin/python3

import sys
import os
sys.path.append(os.path.join(sys.path[0], os.getcwd() + '/python'))

from pynput import mouse, keyboard
import time

import RunescapeWindow

#**************************************************************************
def onMove(x, y):
    x = x - cornerOffset[0]
    y = y - cornerOffset[1]
    if x < 0 or y < 0:
        print("outside of window area")
    elif x > bottomCorner[0] or y > bottomCorner[0]:
        print("outside of window area")
    else:
        print((x, y))

window = RunescapeWindow.RunescapeWindow()
cornerOffset = window.cornerGet()
size = window.sizeGet()
bottomCorner = (cornerOffset[0] + size[0], cornerOffset[1] + size[1])
mouseListener = mouse.Listener(
    on_move=onMove,
    on_click=None,
    on_scroll=None
)

mouseListener.start()
while True:
    time.sleep(5)
mouseListener.stop()
