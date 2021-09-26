import threading
import queue
import numpy as np
import time
import cv2

STATE_RESET = 0
STATE_KILL = 1

class BackgroundSubtractor:
    def __init__(self, window, debug):
        self.window = window
        self.debug = debug
        self.running = True
        self.backgroundSubtractor = cv2.createBackgroundSubtractorMOG2()
        self.mutex = threading.Lock()
        self.backgroundQueue = queue.Queue()
        self.backgroundThread = threading.Thread(target=self.backgroundAccumulate)
        self.backgroundThread.start()
        self.backgroundStateThread = threading.Thread(target=self.stateHandle)
        self.backgroundStateThread.start()
        self.currentFrame = None
        time.sleep(1)

    def __del__(self):
        self.backgroundQueue.put(STATE_KILL)
        self.backgroundThread.join()
        self.backgroundStateThread.join()

    def reset(self):
        self.backgroundQueue.put(STATE_RESET)

    def backgroundAccumulate(self):
        while self.running:
            self.mutex.acquire()
            self.currentFrame = self.backgroundSubtractor.apply(self.window.playAreaGet())
            self.mutex.release()
            if self.debug:
                cv2.imshow('background', self.currentFrame)
                cv2.waitKey(30)
            time.sleep(1 / 30)

    def nextGet(self):
        return np.copy(self.currentFrame)

    def stateHandle(self):
        while self.running:
            nextState = self.backgroundQueue.get()
            if nextState != None:
                if nextState == STATE_RESET:
                    self.mutex.acquire()
                    self.backgroundSubtractor = cv2.createBackgroundSubtractorMOG2()
                    self.mutex.release()
                elif nextState == STATE_KILL:
                    self.running = False
