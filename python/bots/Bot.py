from InputReplay.inputReplay import InputReplay
import random
import time

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

    #**************************************************************************
    def pathReplay(self, pathName):
        if self.paths[pathName] != None:
            self.paths[pathName].replay()

    #**************************************************************************
    def step(self):
        print("step function hasnt been implemented")

    #**************************************************************************
    def idle(self):
        if random.randint(0, 10) > self.idleChance:
            self.window.type(random.choice(self.idleMessages))

        time.sleep(10)
        return STATE_IDLE

    #**************************************************************************
    def inventoryCheck(self):
        inventory = self.window.find('inventory')
        if inventory.full():
            return STATE_BANK_RUN
        else:
            return STATE_MINE
