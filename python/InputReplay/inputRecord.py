#!/usr/bin/python

import sys
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
        self.semaphore = threading.Semaphore(1)
        self.semaphore.acquire()

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
    def escWait(self):
        self.semaphore.acquire()
        self.semaphore.release()

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
        if key != keyboard.Key.esc:
            self.deque.append(Event.KeyPressedEvent(self.timeGet(), key))

    #**************************************************************************
    def onKeyrelease(self, key):
        print("released: " + str(key))
        if key == keyboard.Key.esc:
            self.captureStop()
            self.semaphore.release()

        self.deque.append(Event.KeyReleasedEvent(self.timeGet(), key))

    #**************************************************************************
    def save(self, filename):
        with open(filename, 'wb') as file:
            file.write(pickle.dumps(self.deque))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage python3 inputReplay.py dataFile.dat")
        exit(1)

    filename = sys.argv[1]
    capture = InputRecord()
    input("press enter to start")
    time.sleep(0.2)
    capture.captureStart()
    print("press esc to stop")
    capture.escWait()
    capture.captureStop()

    print("saving")
    capture.save(filename)
