from bots.Bot import *

import cv2
import numpy as np
import math

STATE_MINING = 0
STATE_BANK_RUN = 1
STATE_BANK_DEPOSIT = 2
STATE_MINE_RUN = 3

class Miner(Bot):
    #**************************************************************************
    def __init__(self, profile, window, debug = False):
        self.debug = debug
        super().__init__(profile, window)
        #self.minningLocation = profile.valueGet('minningLocation')
        self.state = STATE_IDLE
        self.mines = {
            'tin':    ([54, 54, 64], [78, 78, 98]),
            'cooper': ([50, 91, 139], [64, 105, 153]),
            #'iron':   ([7, 138, 50], [10, 146, 85]),
            #'gems':   ([150, 223, 61], [151, 235, 169]),
            'bankWindow': ([83, 114, 126], [91, 122, 134]),
            'stairs': ([2, 46, 76], [6, 50, 80])
        }
        self.responTimes = {
            'tin': 3,
            'cooper': 3,
            'iron': 5,
        }
        self.inventoryRange = ([39, 52, 60], [43, 55, 64])
        self.state = STATE_MINING

    #**************************************************************************
    def step(self):
        if self.state == STATE_MINING:
            self.state = self.mine()
        elif self.state == STATE_BANK_RUN:
            self.state = self.bankRun()
        elif self.state == STATE_BANK_DEPOSIT:
            self.state = self.deposit()
        elif self.state == STATE_MINE_RUN:
            self.state = self.mineRun()
        else:
            print("invalid state: " + str(self.state))

    #**************************************************************************
    def inventoryCheck(self):
        inventory = self.window.inventoryAreaGet()
        emptyMask = cv2.inRange(inventory, np.array(self.inventoryRange[0]), np.array(self.inventoryRange[1]))

        inventoryArea = cv2.bitwise_not(emptyMask)
        if self.debug:
            cv2.imshow('inventory', inventoryArea)
            cv2.waitKey(30)

        contours, _ = cv2.findContours(inventoryArea.copy(), 1, 2)
        mineAreas = []
        for next in contours:
            #good for debuging. Draws rectagles over the mines
            x, y, w, h = cv2.boundingRect(next)
            cv2.rectangle(inventoryArea, (x, y), (x+w, y+h), (255, 255, 255), -1)

            #gets number of mines found
            area = cv2.contourArea(next)
            #500 just picked. Might need to adjust this
            if area > 130:
                M = cv2.moments(next)
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                mineAreas.append({'area': area, 'location': (cx, cy)})

        return mineAreas

    #**************************************************************************
    def targetDisplay(self, target):
        debugWindow = self.window.playAreaGet()
        if target != None:
            boundingBox = (target[0] - 50, target[1] - 50, target[0] + 50, target[1] + 50)
            cv2.rectangle(debugWindow, (boundingBox[0], boundingBox[1]), (boundingBox[2], boundingBox[3]), (0, 0, 255))
        else:
            print("no target found")

        cv2.imshow('debug window', debugWindow)
        cv2.waitKey(2000)

    #**************************************************************************
    def inventoryDisplay(self):
        inventory = self.window.inventoryAreaGet()
        emptyMask = cv2.inRange(inventory, np.array(self.inventoryRange[0]), np.array(self.inventoryRange[1]))

        inventoryArea = cv2.bitwise_not(emptyMask)
        cv2.imshow('inventory', inventoryArea)
        cv2.waitKey(30)

    #**************************************************************************
    def mine(self):
        returnState = None

        if len(self.inventoryCheck()) < 27:
            target = self.search('tin')
            if self.debug:
                self.targetDisplay(target)
            self.window.click(target, 'left')
            self.mineWait(self.responTimes['tin'])

            returnState = STATE_MINING
        else:
            returnState = STATE_BANK_RUN

        return returnState

    #**************************************************************************
    def bankRun(self):
        bankMapLocation = (728, 54)
        self.pathReplay('fromtintostairs')
        self.stairsClimb('up')
        self.window.click(bankMapLocation, 'left')

        return STATE_BANK_DEPOSIT

    #**************************************************************************
    def stairsClimb(self, direction):
        upButtonOffset = (0, 44)
        downButtonOffset = (0, 54)
        target = self.search('stairs', areaThreshold=50)
        if self.debug:
            self.targetDisplay(target)
        if direction == 'up':
            #first set of stairs, left click
            target = (target[0] + 20, target[1] + 20)
            self.window.click(target, 'left')
            time.sleep(1)
            #second set of stairs, right click
            target = self.search('stairs', areaThreshold=50)
            if self.debug:
                self.targetDisplay(target)
            target = (target[0] + 20, target[1] + 20)
            self.window.click(target, 'right')
            upButton = (target[0] + upButtonOffset[0], target[1] + upButtonOffset[1])
            self.window.straightClick(upButton, 'left')
        elif direction == 'down':
            #first set of stairs, left click
            target = (target[0] + 40, target[1] - 40)
            self.window.click(target, 'left')
            time.sleep(1)
            #second set of stairs, right click
            target = self.search('stairs', areaThreshold=50)
            if self.debug:
                self.targetDisplay(target)
            target = (target[0] + 20, target[1] + 20)
            self.window.click(target, 'right')
            downButton = (target[0] + downButtonOffset[0], target[1] + downButtonOffset[1])
            self.window.straightClick(downButton, 'left')

        time.sleep(1)



    #**************************************************************************
    def bankDeposit(self):
        depositAllButton = (470, 461)
        bankCloseButton = (510, 35)
        #find bank window
        target = self.search('bankWindow', areaThreshold=100)
        #click on bank window
        if self.debug:
            self.targetDisplay(target)
        self.window.click(target, 'left')
        time.sleep(1)
        #click on deposit all button
        self.window.click(depositAllButton, 'left')
        time.sleep(1)
        #close bank window
        self.window.click(bankCloseButton, 'left')

        return STATE_MINE_RUN

    #**************************************************************************
    def mineRun(self):
        stairsLocation = (700, 144)
        self.window.click(stairsLocation, 'left')
        time.sleep(5)
        self.stairsClimb('down')
        self.pathReplay('frombanktotin')

        return STATE_MINING

    #**************************************************************************
    def mineWait(self, respondTime):
        mining = True
        currentNum = len(self.inventoryCheck())

        endTime = time.time() + 15
        while mining:
            numItems = len(self.inventoryCheck())
            if numItems > currentNum:
                mining = False
            #make sure it doesnt break if someone mines it before we do
            elif time.time() > endTime:
                mining = False
            else:
                time.sleep(1)

        time.sleep(respondTime)

    #**************************************************************************
    def search(self, targetMine, areaThreshold = 200):
        return self.mineFindClosest(targetMine, self.window.playAreaGet(), areaThreshold)

    #**************************************************************************
    def mineFindAll(self, mineType, playArea, areaThreshold):
        mask = cv2.inRange(playArea, np.array(self.mines[mineType][0]), np.array(self.mines[mineType][1]))
        cv2.imshow('mask', mask)
        kernel = np.ones((10, 10), np.uint8)
        closing = cv2.morphologyEx(mask.copy(), cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(closing.copy(), 1, 2)
        mineAreas = []
        for next in contours:
            #good for debuging. Draws rectagles over the mines
            x, y, w, h = cv2.boundingRect(next)
            cv2.rectangle(closing, (x, y), (x+w, y+h), (255, 255, 255), -1)

            #gets number of mines found
            area = cv2.contourArea(next)
            #500 just picked. Might need to adjust this
            if area > areaThreshold:
                M = cv2.moments(next)
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                mineAreas.append({'area': area, 'location': (cx, cy)})

        return mineAreas


    #**************************************************************************
    def mineFindClosest(self, mineType, playArea, areaThreshold):
        mines = self.mineFindAll(mineType, playArea, areaThreshold)

        if len(mines) > 0:
            closest = 10000
            target = ()
            playAreaShape = self.window.playAreaGet().shape
            playerX = (playAreaShape[0] / 2) + 50
            playerY = (playAreaShape[1] / 2) + 50
            for next in mines:
                mineLocation = next['location']
                distance = math.sqrt((playerX - mineLocation[0])**2 + (playerY - mineLocation[1])**2)
                if distance < closest:
                    closest = distance
                    target = mineLocation
            return target
        else:
            return None

    #**************************************************************************
    def mineFindRandom(self, mineType, playArea, areaThreshold):
        mines = self.mineFindAll(mineType, playArea, areaThreshold)

        if len(mines) > 0:
            return random.choice(mines)['location']
        else:
            return None
