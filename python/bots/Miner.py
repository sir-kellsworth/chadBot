from bots.Bot import *
import pytesseract as tess
from PIL import Image

STATE_MINING = 0
STATE_EVENT_WAIT = 1
STATE_RANDOM_EVENT_DISMISS = 2
STATE_BANK_RUN = 3
STATE_BANK_DEPOSIT = 4
STATE_MINE_RUN = 5

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
        #self.red = bots.RandomEventDetection.RandomEventDetection(window, self.randomEventHandle)
        self.randomEventLocation = None
        self.targetedMine = profile.targetGet()
        self.bankType = profile.bankTypeGet()
        self.numStairs = profile.numStairsGet()
        super().__init__(profile, window)
        #self.minningLocation = profile.valueGet('minningLocation')
        self.state = STATE_IDLE
        self.targetColorRanges = {
            'tin':          ([54, 54, 64], [78, 78, 98]),
            'copper':       ([40, 85, 130], [64, 105, 153]),
            'gold':         ([30, 111, 130], [50, 135, 154]),
            'clay':         ([40, 103, 128], [98, 161, 196]),
            #'iron':        ([7, 138, 50], [10, 146, 85]),
            #'gems':        ([150, 223, 61], [151, 235, 169]),
            'bankWindow':   ([99, 112, 122], [111, 150, 140]),
            'bankChest':    ([35, 53, 78], [45, 63, 88]),
            'banker':       ([2, 49, 71], [6, 53, 75]),
            'stairs':       ([2, 46, 76], [6, 50, 80])
        }
        self.mineAreas = {
            'tin':          170,
            'copper':       40,
            'gold':         170,
            'clay':         60,
            'bankWindow':   10,
            'bankChest':    20,
            'banker':       20
        }
        self.mineTimes = {
            'tin':          15,
            'copper':       15,
            'gold':         40,
            'clay':         5,
        }
        self.responTimes = {
            'tin':          2.5,
            'copper':       2.5,
            'iron':         5,
            'gold':         30,
            'clay':         0.5
        }
        self.inventoryRange = ([39, 52, 60], [43, 55, 64])
        self.textRange = ([0, 150, 150], [30, 256, 256])
        self.state = STATE_MINING
        self.clayMine = cv2.imread('templates/clayOre.png', 0)
        self.emptyClayMine = cv2.imread('templates/emptyClayOre.png', 0)
        self.dismissText = cv2.imread('templates/dismissText.png', 0)

    #**************************************************************************
    # description
    #   right clicks on what should be the random event, waits a second,
    #   then clicks on the dismiss event button
    def randomEventDismiss(self):
        target = (self.randomEventLocation[0] + 20, self.randomEventLocation[1] + 50)
        self.window.straightClick(target, 'right')
        waiting = True
        endTime = time.time() + 5
        time.sleep(0.4)
        while waiting:
            playArea = self.window.screenGet()
            dismissMessage = self.window.imageMatch(playArea, self.dismissText, threshold=0.75)
            if time.time() > endTime:
                waiting = False
            elif dismissMessage == None:
                time.sleep(0.4)
            else:
                waiting = False
        #if its not none, then its a random event
        if dismissMessage != None:
            self.targetDisplay(dismissMessage)
            self.window.straightClick(dismissMessage['center'], 'left')
            time.sleep(0.5)
        else:
            self.window.mouse.onlyClick('left')

        return STATE_MINING

    #**************************************************************************
    # description
    #   preforms the next step in the state machine
    def step(self):
        if self.state == STATE_MINING:
            self.state = self.mine()
        elif self.state == STATE_EVENT_WAIT:
            self.state = self.eventWait()
        elif self.state == STATE_RANDOM_EVENT_DISMISS:
            self.state = self.randomEventDismiss()
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
    #   displays the mask of the inventory in a window called 'inventory mask'
    def inventoryDisplay(self):
        inventory = self.window.inventoryAreaGet()
        emptyMask = cv2.inRange(inventory, np.array(self.inventoryRange[0]), np.array(self.inventoryRange[1]))

        inventoryArea = cv2.bitwise_not(emptyMask)
        if self.debug:
            cv2.imshow('inventory mask', inventoryArea)
            cv2.waitKey(30)

    #**************************************************************************
    # description
    #   checks to see if the inventory is full. If not, it searches for tin and mines it
    # returns
    #   type        - int
    #   description - the next state
    def mine(self):
        returnState = None

        if self.numItemsGet() < 28:
            target = None
            while target == None:
                background = self.window.playAreaGet()
                target = self.window.imageMatch(background, self.clayMine, threshold=0.8)
            self.targetDisplay(target)
            self.window.straightClick(self.randomPointSelect(target), 'left', duration=0.05)

            returnState = STATE_EVENT_WAIT
        else:
            returnState = STATE_BANK_RUN

        return returnState

    #**************************************************************************
    # description
    #   waits for either a random event, mining to finish or a timeout in case
    #   something weird happens
    # returns:
    #
    def eventWait(self):
        waiting = True
        nextState = None
        waitForFull = False

        endTime = time.time() + self.mineTimes[self.targetedMine]
        while waiting:
            background = self.window.playAreaGet()
            emptyTarget = self.window.imageMatch(background, self.emptyClayMine, threshold=0.8)
            target = self.window.imageMatch(background, self.clayMine, threshold=0.8)
            randomEvent = self.randomEventDetect(background)
            if randomEvent != None:
                nextState = STATE_RANDOM_EVENT_DISMISS
                self.randomEventLocation = randomEvent['center']
                waiting = False
            elif emptyTarget != None:
                waitForFull = True
            elif waitForFull and target != None:
                nextState = STATE_MINING
                waiting = False
            elif time.time() > endTime:
                nextState = STATE_MINING
                waiting = False

            time.sleep(0.1)

        return nextState

    ###########################################################################
    # description
    #   detects a random event npc in the background
    def randomEventDetect(self, background):
        randomEvent = None
        gray = cv2.inRange(background, np.array(self.textRange[0]), np.array(self.textRange[1]))
        rectKernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9,3))
        gray = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, rectKernel)
        _, gray = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        kernel = np.ones((10, 10), np.uint8)
        final = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(final, 1, 2)
        for next in contours:
            x, y, w, h = cv2.boundingRect(next)

            if w > 30:
                if self.debug:
                    cv2.imshow('texts', background)
                    cv2.waitKey(30)

                randomEvent = {'center': (x + (w // 2), y + (h // 2)), 'size': (w, h)}
                return randomEvent

        return randomEvent

    #**************************************************************************
    # description
    #   runs to the bank and positions in front of the teller
    # returns
    #   type        - int
    #   description - the next state
    def bankRun(self):
        size = self.window.sizeGet()
        self.pathReplay('fromminetobank')
        time.sleep(2)
        if self.numStairs != 0:
            bankMapLocation = (748, 74)
            bankMapLocationScaled = (bankMapLocation[0] / size[0], bankMapLocation[1] / size[1])
            print("**********")
            print("bank map button scaled: " + str(bankMapLocationScaled))
            print("**********")
            self.stairsClimb('up', 2)
            self.window.click(bankMapLocationScaled, 'left')
            time.sleep(8)

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
        upButtonOffset = (0, 34)
        downButtonOffset = (0, 54)

        target = self.search('stairs', areaThreshold=50)
        center = target['center']
        self.targetDisplay(target)
        if isSingleDirection:
            if direction == 'up':
                center = (center[0] + 20, center[1] + 20)
            else:
                center = (center[0] + 60, center[1] - 30)
            self.window.absoluteClick(center, 'left')
        else:
            center = (center[0] + 20, center[1] + 20)
            self.window.absoluteClick(center, 'right')
            if direction == 'up':
                button = (center[0] + upButtonOffset[0], center[1] + upButtonOffset[1])
            else:
                button = (center[0] + downButtonOffset[0], center[1] + downButtonOffset[1])

            self.window.straightClick(button, 'left')

        time.sleep(2)

    #**************************************************************************
    # description
    #   deposits everything in the inventory into the bank
    #   some banks are banks and others are chests. This is defined in the config
    def bankDeposit(self):
        #find bank window
        target = self.search(self.bankType, areaThreshold=self.mineAreas[self.bankType])
        #click on bank window
        self.targetDisplay(target)
        self.window.absoluteClick(self.randomPointSelect(target), 'left')
        time.sleep(5)
        #click on deposit all button
        background = self.window.screenGet()
        depositAll = self.window.imageMatch(background, self.window.templates['bankDepositAll'], threshold=0.6)
        self.targetDisplay(depositAll)
        self.window.absoluteClick(depositAll['center'], 'left')
        time.sleep(1)
        closeBank = self.window.imageMatch(background, self.window.templates['bankExitButton'])
        self.window.absoluteClick(closeBank['center'], 'left')

        return STATE_MINE_RUN

    #**************************************************************************
    # description
    #   runs from the bank, down the stairs and back to the mine
    # returns
    #   type        - int
    #   description - the next state
    def mineRun(self):
        size = self.window.sizeGet()
        if self.numStairs != 0:
            stairsLocation = (720, 164)
            stairsLocationScaled = (stairsLocation[0] / size[0], stairsLocation[1] / size[1])
            print("**********")
            print("stairs location button scaled: " + str(stairsLocationScaled))
            print("**********")
            self.window.click(stairsLocationScaled, 'left')
            time.sleep(9)
            self.stairsClimb('down', 2)
        self.pathReplay('frombanktomine')
        time.sleep(1)

        return STATE_MINING
