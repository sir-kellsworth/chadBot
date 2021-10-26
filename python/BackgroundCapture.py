import threading
import numpy as np
import cv2
from PIL import ImageGrab
import time

class BackgroundCapture:
    def __init__(self, window):
        self.running = True
        self.window = window
        self.corner = (self.window.get_geometry().x, self.window.get_geometry().y)
        self.size = (self.window.get_geometry().width, self.window.get_geometry().height)
        self.backgroundThread = threading.Thread(target=self.run)
        self.backgroundThread.start()
        self.currentImage = None
        time.sleep(1)

    def __del__(self):
        self.running = False
        self.backgroundThread.join()

    def run(self):
        while self.running:
            corner = self.cornerGet()
            size = self.sizeGet()
            #box = (corner[1]:corner[1]+size[1], corner[0]:corner[0]+size[0])
            self.currentImage = np.array(ImageGrab.grab(bbox=(corner[0], corner[1], corner[0]+size[0], corner[1]+size[1])))
            time.sleep(0.3)

    def screenGet(self):
        return self.currentImage

    #**************************************************************************
    # description
    #   returns a pair x,y coordinate of the window corner
    #   this assumes that the window will not be moved
    def cornerGet(self):
        return self.corner

    #**************************************************************************
    # description
    #   returns the size of the runescape window
    #   this assumes that the window will not be moved
    def sizeGet(self):
        return self.size
