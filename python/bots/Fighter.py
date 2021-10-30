from bots.Bot import *
from bots.BackgroundSubtractor import BackgroundSubtractor
from Mouse.IdleMouse import IdleMouse

import cv2
import numpy as np
import math
import threading

STATE_FIGHT_START = 0
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
            'largeEnemy': 350,
            'mediumEnemy': 200,
            'bankWindow': 10,
            'healthBar': 10
        }
        self.inventoryRange = ([39, 52, 60], [43, 55, 64])
        self.state = STATE_FIGHT_START

        self.idleMouse = IdleMouse(self.window)

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

        time.sleep(0.3)

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
            target = self.search()
            self.targetDisplay(target)
            center = target['center']
            center = (center[0] + (target['size'][0] // 2), center[1] + (target['size'][1] // 2) + 5)
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
    def search(self):
        searching = True
        while searching:
            playArea = self.window.playAreaGet()
            for targetName, targetTemplate in self.templates.items():
                targetArea = self.window.imageMatch(playArea, targetTemplate, threshold=0.69)
                if targetArea != None:
                    searching = False
                    break
            if searching:
                time.sleep(0.2)

        return targetArea

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
    #   returns if the health bar is above the players head or not
    # returns
    #   type        - bool
    #   description - True if health bar is detected
    def isFighting(self):
        playArea = self.window.playAreaGet()
        healthTop = playArea.shape[0] // 2 + 40
        healthBottom = healthTop + 40
        healthLeft = playArea.shape[1] // 2 + 60
        healthRight = healthLeft + 60
        playerHealth = playArea[healthTop:healthBottom, healthLeft:healthRight]
        if self.debug:
            cv2.imshow('health', playerHealth)
            cv2.waitKey(10)

        healthBars = self.targetFindAll('healthBar', playerHealth, areaThreshold=self.targetAreas['healthBar'])

        return len(healthBars) == 1


    #**************************************************************************
    # description
    #   waits for the fighting to start. Eventually needs to wait for the background
    #   to settle, or for some timeout before moving on
    # returns
    #   type        - int
    #   description - the next state
    def targetTrack(self):
        #waits a little to make sure we are attacking
        startTime = time.time()
        currentTime = time.time()
        while currentTime - startTime < 10:
            if self.isFighting():
                return STATE_FIGHT_FINISH
            time.sleep(0.2)
            currentTime = time.time()

        return STATE_FIGHT_START

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
        while self.isFighting():
            time.sleep(0.5)

        self.idleMouse.idleStop()

        return STATE_FIGHT_START
