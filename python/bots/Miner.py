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
        self.targetedMine = profile.targetGet()
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
        self.mineAreas = {
            'tin': 170,
            'cooper': 100
        }
        self.responTimes = {
            'tin': 2.5,
            'cooper': 1.5,
            'iron': 5,
        }
        self.inventoryRange = ([39, 52, 60], [43, 55, 64])
        self.state = STATE_MINING

    #**************************************************************************
    # description
    #   preforms the next step in the state machine
    def step(self):
        if self.state == STATE_MINING:
            self.state = self.mine()
        elif self.state == STATE_BANK_RUN:
            self.state = self.bankRun()
        elif self.state == STATE_BANK_DEPOSIT:
            self.state = self.bankDeposit()
        elif self.state == STATE_MINE_RUN:
            self.state = self.mineRun()
        else:
            print("invalid state: " + str(self.state))

    #**************************************************************************
    # description
    #   returns the number of items in the inventory
    def numItemsGet(self):
        return len(self.inventoryCheck())

    #**************************************************************************
    # description
    #   returns a list of locations of all of the items in the inventory
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
    # description
    #   displays a box around the target in a window called 'debug window'
    # parameters
    #   target
    #       type        - pair of x,y coordinates
    #       description - x,y coordinates to draw a box around to show what the bot is targeting
    def targetDisplay(self, target):
        debugWindow = self.window.playAreaGet()
        if target != None:
            boundingBox = (target[0] - 50, target[1] - 50, target[0] + 50, target[1] + 50)
            cv2.rectangle(debugWindow, (boundingBox[0], boundingBox[1]), (boundingBox[2], boundingBox[3]), (0, 0, 255))
            cv2.imshow('debug window', debugWindow)
            cv2.waitKey(30)

    #**************************************************************************
    # description
    #   displays the mask of the inventory in a window called 'inventory mask'
    def inventoryDisplay(self):
        inventory = self.window.inventoryAreaGet()
        emptyMask = cv2.inRange(inventory, np.array(self.inventoryRange[0]), np.array(self.inventoryRange[1]))

        inventoryArea = cv2.bitwise_not(emptyMask)
        cv2.imshow('inventory mask', inventoryArea)
        cv2.waitKey(30)

    #**************************************************************************
    # description
    #   checks to see if the inventory is full. If not, it searches for tin and mines it
    #returns
    #   type        - int
    #   description - the next state
    def mine(self):
        returnState = None

        if len(self.inventoryCheck()) < 27:
            target = self.search(self.targetedMine, areaThreshold=self.mineAreas[self.targetedMine])
            if self.debug:
                self.targetDisplay(target)
            self.window.absoluteClick(target, 'left')
            self.mineWait(self.responTimes[self.targetedMine])

            returnState = STATE_MINING
        else:
            returnState = STATE_BANK_RUN

        return returnState

    #**************************************************************************
    # description
    #   runs to the bank and positions in front of the teller
    #returns
    #   type        - int
    #   description - the next state
    def bankRun(self):
        size = self.window.sizeGet()
        bankMapLocation = (728, 54)
        bankMapLocationScaled = (bankMapLocation[0] / size[0], bankMapLocation[1] / size[1])
        print("**********")
        print("bank map button scaled: " + str(bankMapLocationScaled))
        print("**********")
        self.pathReplay('fromtintobank')
        time.sleep(1)
        self.stairsClimb('up', 2)
        self.window.click(bankMapLocationScaled, 'left')
        time.sleep(10)

        return STATE_BANK_DEPOSIT

    #**************************************************************************
    # description
    #   climbs up or down 2 sets of stairs
    # parameters
    #   direction
    #       type        - string
    #       descriptoin - either 'up' or 'down'. Only works with double stairs
    def stairsClimb(self, direction, numFlights):
        #first flight should always be single direction
        self.flightClimb(direction, True)
        if numFlights > 1:
            for i in range(numFlights-1):
                self.flightClimb(direction, False)

    #**************************************************************************
    # description
    #   climbs up or down a flight of stairs
    # parameters
    #   direction
    #       type        - string
    #       descriptoin - either 'up' or 'down'
    #   isSingleDirection
    #       type        - bool
    #       description - single direction is either stairs at the bottom or top floor.
    #                     not single direction is a mid-floor that could go either way
    def flightClimb(self, direction, isSingleDirection):
        upButtonOffset = (0, 44)
        downButtonOffset = (0, 54)

        target = self.search('stairs', areaThreshold=50)
        self.targetDisplay(target)
        if isSingleDirection:
            if direction == 'up':
                target = (target[0] + 20, target[1] + 20)
            else:
                target = (target[0] + 60, target[1] - 40)
            self.window.absoluteClick(target, 'left')
        else:
            target = (target[0] + 20, target[1] + 20)
            self.window.absoluteClick(target, 'right')
            if direction == 'up':
                button = (target[0] + upButtonOffset[0], target[1] + upButtonOffset[1])
            else:
                button = (target[0] + downButtonOffset[0], target[1] + downButtonOffset[1])

            self.window.straightClick(button, 'left')

        time.sleep(2)

    #**************************************************************************
    # description
    #   deposits everything in the inventory into the bank
    def bankDeposit(self):
        size = self.window.sizeGet()
        depositAllButton = (470, 461)
        depositAllButtonScaled = (depositAllButton[0] / size[0], depositAllButton[1] / size[1])
        print("**********")
        print("deposit all button scaled: " + str(depositAllButtonScaled))
        print("**********")
        bankCloseButton = (510, 35)
        bankCloseButtonScaled = (bankCloseButton[0] / size[0], bankCloseButton[1] / size[1])
        print("**********")
        print("deposit all button scaled: " + str(bankCloseButtonScaled))
        print("**********")
        #find bank window
        target = self.search('bankWindow', areaThreshold=100)
        #click on bank window
        if self.debug:
            self.targetDisplay(target)
        self.window.absoluteClick(target, 'left')
        time.sleep(2)
        #click on deposit all button
        self.window.click(depositAllButtonScaled, 'left')
        time.sleep(1)
        #close bank window
        self.window.click(bankCloseButtonScaled, 'left')

        return STATE_MINE_RUN

    #**************************************************************************
    # description
    #   runs from the bank, down the stairs and back to the mine
    #returns
    #   type        - int
    #   description - the next state
    def mineRun(self):
        size = self.window.sizeGet()
        stairsLocation = (700, 144)
        stairsLocationScaled = (stairsLocation[0] / size[0], stairsLocation[1] / size[1])
        print("**********")
        print("stairs location button scaled: " + str(stairsLocationScaled))
        print("**********")
        self.window.click(stairsLocationScaled, 'left')
        time.sleep(10)
        self.stairsClimb('down', 2)
        self.pathReplay('frombanktotin')
        time.sleep(1)

        return STATE_MINING

    #**************************************************************************
    # description
    #   waits for the mine to respond, then checks to make sure its there again.
    #   if the mining process takes longer than 15 seconds, then it just returns
    # parameters
    #   respondTime
    #       type        - int
    #       description - how long to wait before returning
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
                time.sleep(0.3)

        time.sleep(respondTime)

    #**************************************************************************
    # description
    #   searches for the targeted mine. For now just does a simple pixel search.
    #   might need to do roaming later
    # parameters
    #   targetMine
    #       type        - string
    #       description - name of the 'self.mine' type to search for
    #   areaThreshold
    #       type        - int
    #       description - minimum area of contour to look for
    #returns
    #   type        - pair of x,y
    #   description - window coordinates of where the targeted mine is
    def search(self, targetMine, areaThreshold = 200):
        found = None
        while found == None:
            found = self.mineFindClosest(targetMine, self.window.playAreaGet(), areaThreshold)

        return found

    #**************************************************************************
    # description
    #   searches for the targeted mine. Returns all locations it finds
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
    #returns
    #   type        - list of pair of x,y
    #   description - window coordinates of all mines found
    def mineFindAll(self, mineType, playArea, areaThreshold):
        mask = cv2.inRange(playArea, np.array(self.mines[mineType][0]), np.array(self.mines[mineType][1]))
        cv2.imshow('mask', mask)
        kernel = np.ones((10, 10), np.uint8)
        closing = cv2.morphologyEx(mask.copy(), cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(closing.copy(), 1, 2)
        mineAreas = []
        for next in contours:
            #good for debuging. Draws rectagles over the mines
            if self.debug:
                x, y, w, h = cv2.boundingRect(next)
                cv2.rectangle(closing, (x, y), (x+w, y+h), (255, 255, 255), -1)
                cv2.imshow('mask', closing)

            #gets number of mines found
            area = cv2.contourArea(next)
            if area > areaThreshold:
                M = cv2.moments(next)
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                mineAreas.append({'area': area, 'location': (cx, cy)})

        return mineAreas


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
    #returns
    #   type        - pair of x,y
    #   description - window coordinates of the closest mines found
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
    # description
    #   searches for the targeted mine. Returns random location it finds
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
    #returns
    #   type        - pair of x,y
    #   description - window coordinates of random mine found
    def mineFindRandom(self, mineType, playArea, areaThreshold):
        mines = self.mineFindAll(mineType, playArea, areaThreshold)

        if len(mines) > 0:
            return random.choice(mines)['location']
        else:
            return None
