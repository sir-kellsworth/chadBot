from bots.Bot import *

import cv2
import numpy as np
import math

class Miner(Bot):
    #**************************************************************************
    def __init__(self, profile, window):
        super().__init__(profile, window)
        #self.minningLocation = profile.valueGet('minningLocation')
        self.state = STATE_IDLE
        self.mines = {
            'tin1':   ([0, 13, 104], [3, 73, 148]),
            'tin':    ([54, 54, 64], [78, 78, 98]),
            'cooper': ([14, 135, 88],[15, 140, 169]),
            'iron':   ([7, 138, 50], [10, 146, 85]),
            'gems':   ([150, 223, 61], [151, 235, 169])
        }
        self.responTimes = {
            'tin': 4
        }
        self.inventoryRange = ([39, 52, 60], [43, 55, 64])

    #**************************************************************************
    def stepTest(self):
        if len(self.inventoryCheck()) < 27:
            target = self.search('tin')
            self.targetDisplay(target)
            self.inventoryDisplay()
            self.mine(target)
            self.mineWait(self.responTimes['tin'])
        else:
            print("inventory full")
            self.pathReplay('fromtintobanktotin')
            #self.pathReplay('fromTinToBank')
            #self.pathReplay('bankDeposit')
            #self.pathReplay('fromBankToTin')

    #**************************************************************************
    def inventoryCheck(self):
        inventory = self.window.inventoryAreaGet()
        emptyMask = cv2.inRange(inventory, np.array(self.inventoryRange[0]), np.array(self.inventoryRange[1]))

        inventoryArea = cv2.bitwise_not(emptyMask)
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
            print("no tin found")

        cv2.imshow('debug window', debugWindow)
        cv2.waitKey(100)

    #**************************************************************************
    def inventoryDisplay(self):
        inventory = self.window.inventoryAreaGet()
        emptyMask = cv2.inRange(inventory, np.array(self.inventoryRange[0]), np.array(self.inventoryRange[1]))

        inventoryArea = cv2.bitwise_not(emptyMask)
        cv2.imshow('inventory', inventoryArea)
        cv2.waitKey(30)

    #**************************************************************************
    def step(self):
        if self.state == STATE_IDLE:
            self.idle()
        elif self.state == STATE_MINE_SEARCH:
            self.search(self.targetLocation)
        elif self.state == STATE_MINE:
            self.mine()
        elif self.state == STATE_MINE_FINISH:
            self.mineWait()
        elif self.state == STATE_INVENTORY_CHECK:
            self.inventoryCheck()
        elif self.state == STATE_BANK_RUN:
            self.search(self.window.find('bankLocation'))

    #**************************************************************************
    def mine(self, mineLocation):
        #mine = self.mineFind(self, self.targetMine, self.window.playWindowGet(), self.window)
        self.window.click(mineLocation, 'left')

        return STATE_MINE_FINISH

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
    def search(self, targetMine):
        return self.mineFindClosest(targetMine, self.window.playAreaGet())

    #**************************************************************************
    def mineFindAll(self, mineType, playArea):
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
            if area > 200:
                M = cv2.moments(next)
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                mineAreas.append({'area': area, 'location': (cx, cy)})

        return mineAreas


    #**************************************************************************
    def mineFindClosest(self, mineType, playArea):
        mines = self.mineFindAll(mineType, playArea)

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
    def mineFindRandom(self, mineType, playArea):
        mines = self.mineFindAll(mineType, playArea)

        if len(mines) > 0:
            return random.choice(mines)['location']
        else:
            return None
