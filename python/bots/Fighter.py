from bots.Bot import *

import cv2
import numpy as np
import math

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
        self.target = 'cow'#profile.targetGet()
        super().__init__(profile, window)
        self.targetColorRanges = {
            'cow':    ([52, 58, 70], [60, 66, 78]),
            'bankWindow': ([99, 112, 122], [111, 150, 140]),
            'stairs': ([2, 46, 76], [6, 50, 80]),
            'healthBar': ([0, 255, 0], [0, 255, 0])
        }
        self.targetAreas = {
            'cow': 100,
            'bankWindow': 10,
            'healthBar': 10
        }
        self.inventoryRange = ([39, 52, 60], [43, 55, 64])
        self.state = STATE_FIGHTING

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
            center = (center[0] + 10, center[1] + 15)
            self.window.absoluteClick(center, 'left')
            time.sleep(5)
            self.fightWait()

            returnState = STATE_FIGHTING
        else:
            returnState = STATE_HEAL

        return returnState

    def search(self, target, areaThreshold):
        moving = True
        frames = 0
        targetArea = super().search(target, areaThreshold)
        time.sleep(0.03)

        while moving:
            newTarget = self.targetFindClosest(target, self.window.playAreaGet(), areaThreshold)
            if newTarget == None:
                targetArea = super().search(target, areaThreshold)
                continue

            if targetArea['center'][0] - newTarget['center'][0] < 1:
                frames += 1

            if frames == 3:
                moving = False
            else:
                time.sleep(0.03)

        return targetArea

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
