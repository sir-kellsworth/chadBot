from bots.Bot import *

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
        self.bankType = profile.bankTypeGet()
        self.numStairs = profile.numStairsGet()
        super().__init__(profile, window)
        #self.minningLocation = profile.valueGet('minningLocation')
        self.state = STATE_IDLE
        self.targetColorRanges = {
            'tin':          ([54, 54, 64], [78, 78, 98]),
            'copper':       ([40, 85, 130], [64, 105, 153]),
            'gold':         ([30, 111, 130], [50, 135, 154]),
            'clay':         ([50, 113, 138], [98, 151, 196]),
            #'iron':        ([7, 138, 50], [10, 146, 85]),
            #'gems':        ([150, 223, 61], [151, 235, 169]),
            'bankWindow':   ([99, 112, 122], [111, 150, 140]),
            'bankChest':    ([35, 53, 78], [45, 63, 88]),
            'stairs':       ([2, 46, 76], [6, 50, 80])
        }
        self.mineAreas = {
            'tin':          170,
            'copper':       40,
            'gold':         170,
            'clay':         60,
            'bankWindow':   10,
            'bankChest':    20
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

        if self.numItemsGet() < 27:
            target = self.search(self.targetedMine, areaThreshold=self.mineAreas[self.targetedMine])
            self.targetDisplay(target)
            self.window.straightClick(self.randomPointSelect(target), 'left')
            self.mineWait(self.responTimes[self.targetedMine])

            returnState = STATE_MINING
        else:
            returnState = STATE_BANK_RUN

        return returnState

    #**************************************************************************
    # description
    #   runs to the bank and positions in front of the teller
    # returns
    #   type        - int
    #   description - the next state
    def bankRun(self):
        size = self.window.sizeGet()
        self.pathReplay('fromminetobank')
        time.sleep(3)
        if self.numStairs != 0:
            bankMapLocation = (748, 74)
            bankMapLocationScaled = (bankMapLocation[0] / size[0], bankMapLocation[1] / size[1])
            print("**********")
            print("bank map button scaled: " + str(bankMapLocationScaled))
            print("**********")
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
        time.sleep(2)
        #click on deposit all button
        background = self.window.screenGet()
        depositAll = self.window.imageMatch(background, self.window.templates['bankDepositAll'])
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
        time.sleep(3)

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
        currentNum = self.numItemsGet()

        endTime = time.time() + self.mineTimes[self.targetedMine]
        while mining:
            if self.numItemsGet() > currentNum:
                mining = False
                time.sleep(respondTime)
                return
            #make sure it doesnt break if someone mines it before we do
            if time.time() > endTime:
                mining = False
                return

            time.sleep(0.3)
