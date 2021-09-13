#!/usr/bin/python
import sys
import os
sys.path.append(os.path.join(sys.path[0], '../InputReplay/'))
from pynput import mouse, keyboard
import pyautogui
import time
import threading
import collections
import Event
import pickle

class InputReplay:
    #**************************************************************************
    def __init__(self, filename, window):
        self.windowCorner = window.cornerGet()
        self.windowSize = window.sizeGet()
        with open(filename, 'rb') as file:
            self.goldenCopy = pickle.load(file)

        self.mouseController = mouse.Controller()
        self.keyboardController = keyboard.Controller()

    #**************************************************************************
    def replay(self):
        deque = self.goldenCopy
        lastTime = 0
        for next in deque:
            delayTime = next.timestamp - lastTime
            lastTime = next.timestamp
            self.eventHandle(next)
            time.sleep(delayTime)

    #**************************************************************************
    def eventHandle(self, event):
        if type(event) == Event.MouseMoveEvent:
            self.eventHandleMove(event)
        elif type(event) == Event.MouseClickEvent:
            self.eventHandleClick(event)
        elif type(event) == Event.MouseScrollEvent:
            self.eventHandleScroll(event)
        elif type(event) == Event.KeyPressedEvent:
            self.eventHandleKeyPressed(event)
        elif type(event) == Event.KeyReleasedEvent:
            self.eventHandleKeyReleased(event)

    #**************************************************************************
    def eventHandleMove(self, event):
        location = (
            (event.location[0] * self.windowSize()[0]) + self.windowCorner()[0],
            (event.location[1] * self.windowSize()[1]) + self.windowCorner()[1]
        )
        pyautogui.moveTo(location, _pause=False)#, duration=0.05

    #**************************************************************************
    def eventHandleClick(self, event):
        if event.pressed:
            self.mouseController.press(event.button)
        else:
            self.mouseController.release(event.button)

    #**************************************************************************
    def eventHandleScroll(self, event):
        self.mouseController.scroll(event.scrollDiff[0], event.scrollDiff[1])

    #**************************************************************************
    def eventHandleKeyPressed(self, event):
        self.keyboardController.press(event.key)

    #**************************************************************************
    def eventHandleKeyReleased(self, event):
        self.keyboardController.release(event.key)



if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage python3 inputReplay.py dataFile.dat")
        exit(1)

    filename = sys.argv[1]
    capture = InputReplay(filename)
    capture.replay()
