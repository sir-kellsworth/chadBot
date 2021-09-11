#!/usr/bin/python
import sys
import os
sys.path.append(os.path.join(sys.path[0], 'InputReplay/'))
print(sys.path)
from pynput import mouse, keyboard
import pyautogui
import time
import threading
import collections
import Event
import pickle

class InputReplay:
    #**************************************************************************
    def __init__(self, filename):
        file = open(filename, 'rb')
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
        pyautogui.moveTo(event.location, duration=0.05, _pause=False)

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
    capture = InputReplay("test.csv")
    capture.replay()
