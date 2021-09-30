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
    # description
    #   constructor
    # parameters
    #   window
    #       type        - RunescapeWindow
    #       description - reference to the runescape window to gather info like
    #                       screen size
    def __init__(self, window):
        self.window = window

    #**************************************************************************
    # description
    #   destructor
    def __del__(self):
        self.running = False
        self.backgroundThread.join()

    #**************************************************************************
    # description
    #   starts the idle mouse background animation
    def idleStart(self):
        self.running = True
        self.backgroundThread = threading.Thread(target=self.mouseMove)
        self.backgroundThread.start()

    #**************************************************************************
    # description
    #   stops the idle mouse background animation. Blocks until its done
    def idleStop(self):
        self.running = False
        self.backgroundThread.join()

    #**************************************************************************
    # description
    #   Moves the mouse to a position using a bezel curve
    # parameters
    #   toPosition
    #       type        - (x, y) coordinates
    #       description - coordinates on the screen. Local to the window
    def moveTo(self, toPos):
        fromPos = pyautogui.position()
        curve = HumanCurve(fromPos, toPos)
        for point in curve.points:
            if not self.running:
                break
            pyautogui.moveTo(point)

    #**************************************************************************
    # description
    #   makes little circles on the screen around a point
    # parameters
    #   centerPoint
    #       type        - (x, y) coordinates
    #       description - coordinates of the center of a circle to make with the
    #                       mouse. Coordinates are local to the window
    def circleMake(self, centerPoint):
        radius = 100
        numPoints = 120
        curve = [(math.cos(2*math.pi/numPoints*x)*radius, math.sin(2*math.pi/numPoints*x)*radius) for x in range(0, numPoints)]
        #first point needs some time or it will jump
        point = (int(centerPoint[0] + curve[0][0]), int(centerPoint[1] + curve[0][1]))
        pyautogui.moveTo(point, duration=0.02)
        for point in curve[1:]:
            if not self.running:
                break
            point = (int(centerPoint[0] + point[0]), int(centerPoint[1] + point[1]))
            pyautogui.moveTo(point)

    #**************************************************************************
    # description
    #   called by the backgroundThread. Randomly picks an idle function and
    #   preforms it.If the state changes, then it waits on a mutex until the
    #   state changes back to idling
    def mouseMove(self):
        while self.running:
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
