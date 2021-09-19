from bots.Bot import *

import cv2
import numpy as np
import math
import threading

STATE_FIGHTING = 0
STATE_HEAL = 1

class Fighter(Bot):
    #**************************************************************************
    # description
    #   constructor
    # Parameters:
    #   profile
    #       type        - Profile
    #       description - profile to load paths, what to mine, stuff like that
    #   window
    #       type        - RunescapeWindow
    #       description - window to interact with
    #   debug
    #       type        - boolean
    #       description - used to enable debug windows of what the bot sees
    def __init__(self, profile, window, debug = False):
        self.debug = debug
        self.target = 'cow1'#profile.targetGet()
        super().__init__(profile, window)
        self.targetColorRanges = {
            'cow1':         ([250, 250, 250], [255, 255, 255]),#([37, 53, 70], [60, 66, 78]),
            'cow2':         ([80, 94, 111], [105, 115, 141]),
            'bankWindow':   ([99, 112, 122], [111, 150, 140]),
            'stairs':       ([2, 46, 76], [6, 50, 80]),
            'healthBar':    ([0, 255, 0], [0, 255, 0])
        }
        self.targetAreas = {
            'cow1': 500,
            'cow2': 70,
            'bankWindow': 10,
            'healthBar': 10
        }
        self.inventoryRange = ([39, 52, 60], [43, 55, 64])
        self.state = STATE_FIGHTING

        self.currentFrame = None
        self.running = True
        self.backgroundSubtractor = cv2.createBackgroundSubtractorMOG2()
        self.backgroundThread = threading.Thread(target=self.backgroundAccumulate)
        self.backgroundThread.start()
        time.sleep(1)

    #**************************************************************************
    # description
    #   destructor
    def __del__(self):
        self.running = False
        self.backgroundThread.join()

    #**************************************************************************
    # description
    #   preforms the next step in the state machine
    def step(self):
        if self.state == STATE_FIGHTING:
            self.state = self.fight()
        elif self.state == STATE_HEAL:
            self.state = self.heal()
        else:
            print("invalid state: " + str(self.state))

    #**************************************************************************
    # description
    #   checks to see if the inventory is full. If not, it searches for tin and mines it
    # returns
    #   type        - int
    #   description - the next state
    def fight(self):
        returnState = None

        if self.healthGet() > 3:
            target = self.search(self.target, areaThreshold=self.targetAreas[self.target])
            self.targetDisplay(target)
            center = target['center']
            center = (center[0] + 30, center[1] + 30)
            self.window.straightClick(center, 'left', duration=0)
            time.sleep(5)
            #should make background image while fighting. targets should be obvious after this
            self.backgroundSubtractor = cv2.createBackgroundSubtractorMOG2()
            self.fightWait()

            returnState = STATE_FIGHTING
        else:
            returnState = STATE_HEAL

        return returnState

    #**************************************************************************
    # description
    #   searching playarea for animated target. Basically, it subtracts the background
    # parameters
    #   target
    #       type        - string
    #       description - name of the 'self.mine' type to search for
    #   areaThreshold
    #       type        - int
    #       description - minimum area of contour to look for
    # returns
    #   type        - 'center' - (x,y), 'area' - float and 'size' - (width, height)
    def search(self, target, areaThreshold):
        moving = True
        frames = 0
        targetArea = None
        while targetArea == None:
            nonBackground = np.copy(self.currentFrame)
            targetArea = self.targetFindClosestBackground(target, nonBackground, areaThreshold)
            time.sleep(0.5)

        return targetArea

    #**************************************************************************
    # description
    #   searches for the targeted mine. Returns location closest to the player
    # parameters
    #   mineType
    #       type        - string
    #       description - name of the 'self.mine' type to search for
    #   playArea
    #       type        - np.array
    #       description - area of the window to search
    #   areaThreshold
    #       type        - int
    #       description - minimum area of contour to look for
    # returns
    #   type        - 'center' - (x,y), 'area' - float and 'size' - (width, height)
    #   description - dictionary of 'center', 'area' and 'size'
    def targetFindClosestBackground(self, mineType, playArea, areaThreshold):
        mines = self.targetFindAllBackground(mineType, playArea, areaThreshold)

        if len(mines) > 0:
            closest = 10000
            target = ()
            playAreaShape = self.window.playAreaGet().shape
            playerX = (playAreaShape[0] / 2) + 50
            playerY = (playAreaShape[1] / 2) + 50
            for next in mines:
                mineLocation = next['center']
                distance = math.sqrt((playerX - mineLocation[0])**2 + (playerY - mineLocation[1])**2)
                if distance < closest:
                    closest = distance
                    target = next
            return target
        else:
            return None

    def targetFindAllBackground(self, target, playArea, areaThreshold):
        contours, _ = cv2.findContours(playArea.copy(), 1, 2)
        mineAreas = []
        for next in contours:
            x, y, w, h = cv2.boundingRect(next)
            #good for debuging. Draws rectagles over the mines
            if self.debug:
                cv2.rectangle(playArea, (x, y), (x+w, y+h), (255, 255, 255), -1)
                cv2.imshow('mask', playArea)

            #gets number of mines found
            area = cv2.contourArea(next)
            if area > areaThreshold:
                M = cv2.moments(next)
                centerX = int(M['m10'] / M['m00'])
                centerY = int(M['m01'] / M['m00'])
                mineAreas.append({'area': area, 'center': (centerX, centerY), 'size': (w, h)})

        return mineAreas

    def backgroundAccumulate(self):
        while self.running:
            self.currentFrame = self.backgroundSubtractor.apply(self.window.playAreaGet())
            if self.debug:
                cv2.imshow('background', self.currentFrame)
                cv2.waitKey(30)
            time.sleep(1 / 30)

    def healthGet(self):
        return 10

    #**************************************************************************
    # description
    #   waits for the mine to respond, then checks to make sure its there again.
    #   if the mining process takes longer than 15 seconds, then it just returns
    # parameters
    #   respondTime
    #       type        - int
    #       description - how long to wait before returning
    def fightWait(self):
        fighting = True

        while fighting:
            playArea = self.window.playAreaGet()
            healthBars = self.targetFindAll('healthBar', playArea, areaThreshold=self.targetAreas['healthBar'])
            if len(healthBars) <= 0.1:
                fighting = False
                return

            time.sleep(0.5)
