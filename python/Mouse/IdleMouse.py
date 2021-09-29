import time
import threading
import pyautogui
import pytweening
import queue
import numpy as np
import random
import math
from Mouse.HumanCurve import HumanCurve

STATE_IDLE_START = 0
STATE_IDLE_STOP = 1
STATE_IDLE_KILL = 2

NUM_OPTIONS = 4
ACTION_RANDOM_POINT = 0
ACTION_CENTER = 1
ACTION_CIRCLE = 2
ACTION_NOTHING = 3

class IdleMouse:
    #**************************************************************************
    def __init__(self, window):
        self.window = window
        self.running = True
        self.idling = False
        self.backgroundQueue = queue.Queue()
        self.idlingSemaphore = threading.Semaphore()
        self.stopingSemaphore = threading.Semaphore()
        self.stateThread = threading.Thread(target=self.stateHandle)
        self.stateThread.start()
        self.backgroundThread = threading.Thread(target=self.mouseMove)
        self.backgroundThread.start()

    #**************************************************************************
    def __del__(self):
        self.backgroundQueue.put(STATE_IDLE_KILL)
        self.backgroundThread.join()
        self.stateThread.join()

    #**************************************************************************
    def idleStart(self):
        self.backgroundQueue.put(STATE_IDLE_START)

    #**************************************************************************
    def idleStop(self):
        self.backgroundQueue.put(STATE_IDLE_STOP)
        self.stopingSemaphore.acquire()

    #**************************************************************************
    def moveTo(self, toPos):
        fromPos = pyautogui.position()
        curve = HumanCurve(fromPos, toPos)
        for point in curve.points:
            pyautogui.moveTo(point)

    #**************************************************************************
    def circleMake(self, centerPoint):
        radius = 100
        numPoints = 120
        curve = [(math.cos(2*math.pi/numPoints*x)*radius, math.sin(2*math.pi/numPoints*x)*radius) for x in range(0, numPoints)]
        #first point needs some time or it will jump
        point = (int(centerPoint[0] + curve[0][0]), int(centerPoint[1] + curve[0][1]))
        pyautogui.moveTo(point, duration=0.02)
        for point in curve[1:]:
            point = (int(centerPoint[0] + point[0]), int(centerPoint[1] + point[1]))
            pyautogui.moveTo(point)

    def mouseMove(self):
        while self.running:
            if self.idling:
                moveType = random.randint(0, NUM_OPTIONS)
                corner = self.window.cornerGet()
                size = self.window.sizeGet()
                if moveType == ACTION_RANDOM_POINT:
                    randomPoint = (
                        random.randint(0, size[0]) + corner[0],
                        random.randint(0, size[1]) + corner[1]
                    )
                    self.moveTo(randomPoint)
                elif moveType == ACTION_CENTER:
                    corner = self.window.cornerGet()
                    playAreaSize = self.window.playAreaGet().shape
                    center = (
                        (playAreaSize[0] // 2) + corner[0],
                        (playAreaSize[1] // 2) + corner[1]
                    )
                    self.moveTo(center)
                elif moveType == ACTION_CIRCLE:
                    corner = self.window.cornerGet()
                    playAreaSize = self.window.playAreaGet().shape
                    center = (
                        (playAreaSize[0] // 2) + corner[0],
                        (playAreaSize[1] // 2) + corner[1]
                    )
                    self.circleMake(center)
                elif moveType == ACTION_NOTHING:
                    time.sleep(5)

                time.sleep(0.3)
            else:
                self.stopingSemaphore.release()
                self.idlingSemaphore.acquire()

    #**************************************************************************
    def stateHandle(self):
        while self.running:
            nextState = self.backgroundQueue.get()

            if nextState == STATE_IDLE_START:
                self.idling = True
                self.idlingSemaphore.release()
            elif nextState == STATE_IDLE_STOP:
                self.idling = False
            elif nextState == STATE_IDLE_KILL:
                self.running = False
                self.idling = False
                self.idlingSemaphore.release()
