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

    #**************************************************************************
    def stepTest(self):
        target = self.search('tin')
        self.targetDisplay(target)
        self.mine(target)
        time.sleep(12)

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
    def mineWait(self):
        #for now, just wait some time
        #later, it will check the screen to see if the mine is still there
        mining = True
        target = self.mineFindClosest(self, self.targetMine, self.window.playWindowGet(), self.window)

        #search for mine closest to the player
        while mining:
            mine = self.mineFindClosest(self, self.targetMine, self.window.playWindowGet(), self.window)
            if targetMine != closestMine:
                mining = False
            else:
                time.sleep(5)

        return STATE_INVENTORY_CHECK

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
            playerCenter = self.window.sizeGet()
            playerX = playerCenter[0] / 2
            playerY = playerCenter[1] / 2
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
