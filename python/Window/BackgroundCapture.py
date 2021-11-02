import threading
import numpy as np
import cv2
from PIL import ImageGrab
import time

class BackgroundCapture:
    ###########################################################################
    # description
    #   constructor
    def __init__(self, window):
        self.running = True
        self.window = window
        self.corner = (self.window.get_geometry().x, self.window.get_geometry().y)
        self.size = (self.window.get_geometry().width, self.window.get_geometry().height)
        self.backgroundThread = threading.Thread(target=self.run)
        self.backgroundThread.start()
        self.subscribers = []
        self.timerDelay = 0.4
        time.sleep(1)

    ###########################################################################
    # description
    #   destructor
    def close(self):
        self.running = False
        self.backgroundThread.join()

    #**************************************************************************
    # description
    #   returns a pair x,y coordinate of the window corner
    #   this assumes that the window will not be moved
    def cornerGet(self):
        return self.corner

    ###########################################################################
    # description
    #   background thread to capture the runescape window
    def run(self):
        while self.running:
            corner = self.cornerGet()
            size = self.sizeGet()
            #box = (corner[1]:corner[1]+size[1], corner[0]:corner[0]+size[0])
            window = np.array(ImageGrab.grab(bbox=(corner[0], corner[1], corner[0]+size[0], corner[1]+size[1])))
            window =  cv2.cvtColor(window, cv2.COLOR_BGR2RGB)
            playArea = window[25:500, 25:615]
            inventory = window[330:-85, 631:-9]

            for subscriber in self.subscribers:
                subscriber.windowProcess({
                    'window': window,
                    'playArea': playArea,
                    'inventory': inventory
                })

            time.sleep(self.timerDelay)

    ###########################################################################
    # description
    #   removes the subscriber
    def screenGetUnsubscribe(self, subscriber):
        if subscriber in self.subscribers:
            self.subscribers.remove(subscriber)

    ###########################################################################
    # description
    #   subscribes the object if its not already subscribed
    def screenGetSubscribe(self, subscriber):
        if not subscriber in self.subscribers:
            self.subscribers.append(subscriber)

    #**************************************************************************
    # description
    #   returns the size of the runescape window
    #   this assumes that the window will not be moved
    def sizeGet(self):
        return self.size
