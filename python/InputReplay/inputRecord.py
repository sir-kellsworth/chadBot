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
    def __init__(self, window):
        self.window = window
        self.windowCorner = window.cornerGet()
        self.windowSize = window.sizeGet()
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
        self.running = False
        self.mouseListener.start()
        self.keyboardListener.start()
        self.semaphore = threading.Semaphore(1)
        self.semaphore.acquire()

    #**************************************************************************
    def captureStart(self):
        self.offset = time.time()
        self.running = True
        self.semaphore.acquire()

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
    def mouseInsideWindow(self, mousePoint, windowRect):
        if mousePoint[0] > windowRect[0] and mousePoint[0] < windowRect[0] + windowRect[2]:
            if mousePoint[1] > windowRect[1] and mousePoint[1] < windowRect[1] + windowRect[3]:
                return True

        return False

    #**************************************************************************
    def onMove(self, x, y):
        if self.running and self.mouseInsideWindow((x, y), self.windowRect):
            x = (x - self.windowCorner[0]) / self.windowSize[0]
            y = (y - self.windowCorner[1]) / self.windowSize[1]
            self.deque.append(Event.MouseMoveEvent(self.timeGet(), (x, y)))

    #**************************************************************************
    def onClick(self, x, y, button, pressed):
        if self.running and self.mouseInsideWindow((x, y), self.windowRect):
            x = (x - self.windowCorner[0]) / self.windowSize[0]
            y = (y - self.windowCorner[1]) / self.windowSize[1]
            self.deque.append(Event.MouseClickEvent(self.timeGet(), (x, y), button, pressed))

    #**************************************************************************
    def onScroll(self, x, y, dx, dy):
        if self.running:
            self.deque.append(Event.MouseScrollEvent(self.timeGet(), (x, y), (dx, dy)))

    #**************************************************************************
    def onKeypress(self, key):
        if self.running and key != keyboard.Key.esc:
            self.deque.append(Event.KeyPressedEvent(self.timeGet(), key))

    #**************************************************************************
    def onKeyrelease(self, key):
        if self.running and key == keyboard.Key.esc:
            self.captureStop()
            self.semaphore.release()

        self.deque.append(Event.KeyReleasedEvent(self.timeGet(), key))

    #**************************************************************************
    def save(self, filename):
        with open(filename, 'wb') as file:
            file.write(pickle.dumps(self.deque))
