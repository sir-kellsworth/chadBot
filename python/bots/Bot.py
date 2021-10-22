from InputReplay.inputReplay import InputReplay
import random
import time
import cv2
import numpy as np
import math
import os
import imutils

#states for bots
STATE_IDLE = 0
STATE_MINE_SEARCH = 1
STATE_MINE = 2
STATE_MINE_FINISH = 3
STATE_INVENTORY_CHECK = 4
STATE_BANK_RUN = 5

class Bot:
    #**************************************************************************
    def __init__(self, profile, window):
        self.window = window
        #self.targetLocation = profile.targetLocationGet()
        self.paths = {}
        for path in profile.pathsGet():
            self.paths[path['PathName']] = InputReplay(path['File'], window)
        self.idleMessages = profile.idleMessagesGet()
        self.idleChance = profile.idleChanceGet()
        self.templates = self.templatesLoad(profile.templatesFolderGet())

    #**************************************************************************
    def templatesLoad(self, templateFolder):
        templates = {}
        for root, folders, files in os.walk(templateFolder):
            for file in files:
                fileBase = os.path.splitext(file)[0]
                baseImage = cv2.imread(os.path.join(root, file), 0)
                templates[fileBase] = baseImage
                templates[fileBase + "-rotated90"] = cv2.rotate(baseImage, cv2.ROTATE_90_CLOCKWISE)
                templates[fileBase + "-flipped"] = cv2.flip(baseImage, -1)
                templates[fileBase + "-rotated-90"] = cv2.rotate(baseImage, cv2.ROTATE_90_COUNTERCLOCKWISE)


        return templates

    #**************************************************************************
    # description
    #   replays a saved path that was loaded from config file
    # Parameters
    #   pathName
    #       type        - String
    #       description - name of path. Usually basename of file
    def pathReplay(self, pathName):
        if self.paths[pathName] != None:
            self.paths[pathName].replay()

    #**************************************************************************
    # description
    #   preforms the next step in the state machine
    def step(self):
        print("step function hasnt been implemented")

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
            cv2.waitKey(1)

        contours, _ = cv2.findContours(inventoryArea.copy(), 1, 2)
        mineAreas = []
        for next in contours:
            x, y, w, h = cv2.boundingRect(next)
            #good for debuging. Draws rectagles over the mines
            if self.debug:
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
        if target != None and self.debug:
            center = target['center']
            halfWidth = target['size'][0] // 2
            halfHeight = target['size'][1] // 2
            boundingBox = (center[0] - halfWidth, center[1] - halfHeight, center[0] + halfWidth, center[1] + halfHeight)
            cv2.rectangle(debugWindow, (boundingBox[0], boundingBox[1]), (boundingBox[2], boundingBox[3]), (0, 0, 255))
            cv2.imshow('debug window', debugWindow)
            cv2.waitKey(30)

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
    # returns
    #   type        - 'center' - (x,y), 'area' - float and 'size' - (width, height)
    #   description - dictionary of 'center', 'area' and 'size'
    def search(self, targetMine, areaThreshold = 200):
        found = None
        while found == None:
            found = self.targetFindClosest(targetMine, self.window.playAreaGet(), areaThreshold)

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
    # returns
    #   type        - 'center' - (x,y), 'area' - float and 'size' - (width, height)
    #   description - dictionary of 'center', 'area' and 'size' of closest mine
    def targetFindAll(self, mineType, playArea, areaThreshold):
        mask = cv2.inRange(playArea, np.array(self.targetColorRanges[mineType][0]), np.array(self.targetColorRanges[mineType][1]))
        if self.debug:
            cv2.imshow('mask', mask)
            cv2.waitKey(1)
        kernel = np.ones((10, 10), np.uint8)
        closing = cv2.morphologyEx(mask.copy(), cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(closing.copy(), 1, 2)
        mineAreas = []
        for next in contours:
            x, y, w, h = cv2.boundingRect(next)
            #good for debuging. Draws rectagles over the mines
            if self.debug:
                cv2.rectangle(closing, (x, y), (x+w, y+h), (255, 255, 255), -1)
                cv2.imshow('mask', closing)

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
    def targetFindClosest(self, mineType, playArea, areaThreshold):
        mines = self.targetFindAll(mineType, playArea, areaThreshold)

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
    # returns
    #   type        - pair of x,y
    #   description - window coordinates of random mine found
    def targetFindRandom(self, mineType, playArea, areaThreshold):
        mines = self.mineFindAll(mineType, playArea, areaThreshold)

        if len(mines) > 0:
            return random.choice(mines)
        else:
            return None

    #**************************************************************************
    # description
    #   returns a random point in the target area
    # parameters
    #   target
    #       type        - dict
    #       description - dict from mineFindAll
    # returns
    #   type            - pair of x,y
    #   description     - random coordinates from inside the target rectangle
    def randomPointSelect(self, target):
        center = target['center']
        size = target['size']

        #all of this is to avoid accidentally clicking outside the object bounds
        widthMin = center[0] + (size[0] // 2)
        widthMax = center[0] + (size[0] // 2)
        heightMin = center[1] + (size[1] // 2)
        heightMax = center[1] + (size[1] // 2)
        randomWidth = random.randint(widthMin, widthMax)
        randomHeight = random.randint(heightMin, heightMax)

        return (randomWidth, randomHeight)
