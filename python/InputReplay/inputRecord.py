#!/usr/bin/python

from pynput import mouse, keyboard
import pyautogui
import time
import threading
import collections
import Event
import pickle

class InputRecord:
    #**************************************************************************
    def __init__(self):
        self.deque = collections.deque()
        self.mouseListener = mouse.Listener(
            on_move=self.onMove,
            on_click=self.onClick,
            on_scroll=self.onScroll
        )
        self.mouseController = mouse.Controller()
        self.keyboardListener = keyboard.Listener(
            on_press=self.onKeypress,
            on_release=self.onKeyrelease
        )
        self.keyboardController = keyboard.Controller()

    #**************************************************************************
    def captureStart(self):
        self.offset = time.time()
        self.mouseListener.start()
        self.keyboardListener.start()

    #**************************************************************************
    def captureStop(self):
        self.mouseListener.stop()
        self.keyboardListener.stop()

    #**************************************************************************
    def timeGet(self):
        return time.time() - self.offset

    #**************************************************************************
    def onMove(self, x, y):
        self.deque.append(Event.MouseMoveEvent(self.timeGet(), (x, y)))

    #**************************************************************************
    def onClick(self, x, y, button, pressed):
        self.deque.append(Event.MouseClickEvent(self.timeGet(), (x, y), button, pressed))

    #**************************************************************************
    def onScroll(self, x, y, dx, dy):
        self.deque.append(Event.MouseScrollEvent(self.timeGet(), (x, y), (dx, dy)))

    #**************************************************************************
    def onKeypress(self, key):
        self.deque.append(Event.KeyPressedEvent(self.timeGet(), key))

    #**************************************************************************
    def onKeyrelease(self, key):
        self.deque.append(Event.KeyReleasedEvent(self.timeGet(), key))

    #**************************************************************************
    def save(self, filename):
        with open(filename, 'wb') as file:
            file.write(pickle.dumps(self.deque))


if __name__ == "__main__":
    capture = InputRecord()
    input("press enter to start")
    capture.captureStart()
    input("press enter to stop")
    capture.captureStop()

    print("saving")
    capture.save("test.csv")
