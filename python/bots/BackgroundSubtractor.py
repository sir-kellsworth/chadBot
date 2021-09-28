import threading
import queue
import numpy as np
import time
import cv2

STATE_RESET = 0
STATE_KILL = 1

class BackgroundSubtractor:
    #**************************************************************************
    # description
    #   constructor
    # Parameters:
    #   window
    #       type        - RunescapeWindow
    #       description - window to interact with
    #   debug
    #       type        - boolean
    #       description - used to enable debug windows of what the bot sees
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

    #**************************************************************************
    # description
    #   destructor
    def __del__(self):
        self.backgroundQueue.put(STATE_KILL)
        self.backgroundThread.join()
        self.backgroundStateThread.join()

    #**************************************************************************
    # description
    #   resets the background state
    def reset(self):
        self.backgroundQueue.put(STATE_RESET)

    #**************************************************************************
    # description
    #   background thread that accumulates entire playArea to pickout moving targets
    def backgroundAccumulate(self):
        while self.running:
            self.mutex.acquire()
            self.currentFrame = self.backgroundSubtractor.apply(self.window.playAreaGet())
            self.mutex.release()
            if self.debug:
                cv2.imshow('background', self.currentFrame)
                #waitKey is 1 so, while debugging, it doesnt wait for 2 frames instead of 1
                cv2.waitKey(1)
            time.sleep(1 / 30)

    #**************************************************************************
    # description
    #   returns the next frame in the window
    # returns
    #   type        - np.array
    #   description - copy of the current frame
    def nextGet(self):
        return np.copy(self.currentFrame)

    #**************************************************************************
    # description
    #   background thread to handle switching between the running state,
    #   reset state and kill state
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
