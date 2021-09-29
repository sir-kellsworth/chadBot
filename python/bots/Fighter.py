from bots.Bot import *
from bots.BackgroundSubtractor import BackgroundSubtractor
from Mouse.IdleMouse import IdleMouse

import cv2
import numpy as np
import math
import threading

STATE_FIGHTING = 0
STATE_TARGET_TRACK = 1
STATE_FIGHT_FINISH = 2
STATE_HEAL = 3

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
        self.target = profile.targetGet()
        super().__init__(profile, window)
        self.targetColorRanges = {
            'bankWindow':   ([99, 112, 122], [111, 150, 140]),
            'stairs':       ([2, 46, 76], [6, 50, 80]),
            'healthBar':    ([0, 255, 0], [0, 255, 0])
        }
        self.targetAreas = {
            'cow': 350,
            'bankWindow': 10,
            'healthBar': 10
        }
        self.inventoryRange = ([39, 52, 60], [43, 55, 64])
        self.state = STATE_FIGHTING

        self.subtractor = BackgroundSubtractor(self.window, debug)
        self.idleMouse = IdleMouse(self.window)

    #**************************************************************************
    # description
    #   destructor
    def __del__(self):
        self.running = False

    #**************************************************************************
    # description
    #   preforms the next step in the state machine
    def step(self):
        if self.state == STATE_FIGHT_START:
            self.state = self.fightStart()
        elif self.state == STATE_TARGET_TRACK:
            self.state = self.targetTrack()
        elif self.state == STATE_FIGHT_FINISH:
            self.state = self.fightFinish()
        elif self.state == STATE_HEAL:
            self.state = self.heal()
        else:
            print("invalid state: " + str(self.state))

    #**************************************************************************
    # description
    #   searches for a new target. When one is found, it clicks on it and moves to
    #   the next state
    # returns
    #   type        - int
    #   description - the next state
    def fightStart(self):
        returnState = None

        if self.healthGet() > 3:
            target = self.search(self.target, areaThreshold=self.targetAreas[self.target])
            self.targetDisplay(target)
            center = target['center']
            center = (center[0] + 30, center[1] + 30)
            self.window.straightClick(center, 'left', duration=0)

            returnState = STATE_TARGET_TRACK
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
        searching = True
        while searching:
            nonBackground = self.subtractor.nextGet()
            targetArea = self.targetFindClosestBackground(nonBackground, areaThreshold)
            if targetArea == None:
                time.sleep(0.5)
            else:
                searching = False

        return targetArea

    #**************************************************************************
    # description
    #   searches the background for moving targets closest to the player
    # parameters
    #   nonBackground
    #       type        - np.array
    #       description - area of the window to search
    #   areaThreshold
    #       type        - int
    #       description - minimum area of contour to look for
    # returns
    #   type        - 'center' - (x,y), 'area' - float and 'size' - (width, height)
    #   description - dictionary of 'center', 'area' and 'size'
    def targetFindClosestBackground(self, nonBackground, areaThreshold):
        mines = self.targetFindAllBackground(nonBackground, areaThreshold)

        if len(mines) > 0:
            closest = 10000
            target = ()
            playAreaShape = nonBackground.shape
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

    #**************************************************************************
    # description
    #   searches the background for all moving targets
    # parameters
    #   nonBackground
    #       type        - np.array
    #       description - area of the window to search
    #   areaThreshold
    #       type        - int
    #       description - minimum area of contour to look for
    # returns
    #   type        - 'center' - (x,y), 'area' - float and 'size' - (width, height)
    #   description - list of dictionary of 'center', 'area' and 'size'
    def targetFindAllBackground(self, nonBackground, areaThreshold):
        contours, _ = cv2.findContours(nonBackground.copy(), 1, 2)
        mineAreas = []
        for next in contours:
            x, y, w, h = cv2.boundingRect(next)
            #good for debuging. Draws rectagles over the mines
            if self.debug:
                cv2.rectangle(nonBackground, (x, y), (x+w, y+h), (255, 255, 255), -1)
                cv2.imshow('mask', nonBackground)

            #gets number of mines found
            area = cv2.contourArea(next)
            if area > areaThreshold:
                M = cv2.moments(next)
                centerX = int(M['m10'] / M['m00'])
                centerY = int(M['m01'] / M['m00'])
                mineAreas.append({'area': area, 'center': (centerX, centerY), 'size': (w, h)})

        return mineAreas

    #**************************************************************************
    # description
    #   returns an integer value of the players remaining health
    # returns
    #   type        - int
    #   description - value of player health
    def healthGet(self):
        return 10

    #**************************************************************************
    # description
    #   waits for the fighting to start. Eventually needs to wait for the background
    #   to settle, or for some timeout before moving on
    # returns
    #   type        - int
    #   description - the next state
    def targetTrack(self):
        #should make background image while fighting. targets should be obvious after this
        #also should make it clear when the bot stops moving. The background will reset pretty quickly
        self.subtractor.reset()
        #waits a little to make sure we are attacking
        time.sleep(5)

        return STATE_FIGHT_FINISH

    #**************************************************************************
    # description
    #   waits for the bot to beat the enemy. This is not a smart function.
    #   It waits for the health bars to disapear.
    # returns
    #   type        - int
    #   description - the next state
    def fightFinish(self):
        fighting = True

        self.idleMouse.idleStart()
        while fighting:
            playArea = self.window.playAreaGet()
            healthBars = self.targetFindAll('healthBar', playArea, areaThreshold=self.targetAreas['healthBar'])
            if len(healthBars) <= 1:
                fighting = False
                return

            time.sleep(0.5)

        self.idleMouse.idleStop()

        return STATE_FIGHTING