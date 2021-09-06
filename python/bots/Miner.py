import Bot

import cv2
import numpy as np

class Minner(Bot):
    def __init__(self, profile, window):
        super().__init__(profile, window)
        self.minningLocation = profile.valueGet('minningLocation')
        self.state = STATE_IDLE
        self.mines = {
            'tin1':   ([0, 13, 104], [3, 73, 148]),
            'tin':    ([0, 19, 121], [1, 30, 136]),
            'cooper': ([14, 135, 88],[15, 140, 169]),
            'iron':   ([7, 138, 50], [10, 146, 85]),
            'gems':   ([150, 223, 61], [151, 235, 169])
        }

    def step(self):
        if self.state == STATE_IDEL:
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
    def mine(self):
        mine = self.mineFind(self, self.targetMine, self.window.playWindowGet(), self.window)
        self.window.click(mine.position(), 'leftClick')

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
    def search(self, targetLocation):
        print("search function not implemented yet")
        map = self.window.find('miniMap')
        searching = True

        #search idea:
        #first, use premade path to target
        #second, search for mine
        while searching:
            self.pathReplay(self.targetLocation)
            mine = self.mineFindRandom(self, self.targetMine, self.window.playWindowGet(), self.window)
            self.window.click(mine)
            if mine != None:
                searching = False

        return STATE_MINE

    #**************************************************************************
    def mineFindClosest(self, mineType, playArea, window):
        screenshot = window.get_screenshot_as_png()
        location = playArea.location
        size = playArea.size
        frame = np.frombuffer(screenshot, np.uint8)
        img = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        left = location['x']
        top = location['y']
        right = left + size['width']
        bottom = top + size['height']
        playImage = img[left:right, top:bottom]

        mask = cv2.inRange(playImage, np.array(self.mines[minetype][0], np.array(self.mines[mineType][1])))
        kernel = np.ones((10, 10), np.uint8)
        closing = cv2.morphologyEx(mask.copy(), cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(closing.copy(), 1, 2)
        mineAreas = {}
        for next in contours:
            #good for debuging. Draws rectagles over the mines
            x, y, w, h = cv2.boundingRect(next)
            cv2.rectangle(closing, (x, y), (x+w, y+h), (255, 255, 255), -1)

            #gets number of mines found
            area = cv2.contourArea(next)
            #500 just picked. Might need to adjust this
            if area > 500:
                centerX = x + (w // 2)
                centerY = y + (h // 2)
                mineLocations[area] = (centerX, centerY)

            if len(mineAreas) > 0:
                closest = 10000
                target = ()
                for next in mineAreas:
                    distance = Math.sqrt(Math.square(playerX - centerX) + Math.square(playerY - centerY))
                    if distance < closest:
                        closest = distance
                        target = (centerX, centerY)
                return target
            else:
                return None

    #**************************************************************************
    def mineFindRandom(self, mineType, playArea, window):
        screenshot = window.get_screenshot_as_png()
        location = playArea.location
        size = playArea.size
        frame = np.frombuffer(screenshot, np.uint8)
        img = cv2.imdecode(frame, cv2.IMREAD_COLOR)
        left = location['x']
        top = location['y']
        right = left + size['width']
        bottom = top + size['height']
        playImage = img[left:right, top:bottom]

        mask = cv2.inRange(playImage, np.array(self.mines[minetype][0], np.array(self.mines[mineType][1])))
        kernel = np.ones((10, 10), np.uint8)
        closing = cv2.morphologyEx(mask.copy(), cv2.MORPH_CLOSE, kernel)

        contours, _ = cv2.findContours(closing.copy(), 1, 2)
        mineAreas = {}
        for next in contours:
            #good for debuging. Draws rectagles over the mines
            x, y, w, h = cv2.boundingRect(next)
            cv2.rectangle(closing, (x, y), (x+w, y+h), (255, 255, 255), -1)

            #gets number of mines found
            area = cv2.contourArea(next)
            #500 just picked. Might need to adjust this
            if area > 500:
                M = cv2.moments(next)
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                mineAreas[area] = (cx, cy)

            if len(mineAreas) > 0:
                return random.choice(mineAreas)
            else:
                return None
