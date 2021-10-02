import Xlib
import Xlib.display
import Xlib.X
import time
import subprocess
import numpy as np
import cv2
from PIL import ImageGrab
import random

from Mouse.HumanMouse import HumanMouse
from Keyboard import Keyboard

class RunescapeWindow:
    #**************************************************************************
    # description
    #   constructor
    def __init__(self):
        self.mouse = HumanMouse()
        self.keyboard = Keyboard()
        self.display = Xlib.display.Display()
        self.window = self.windowSearch()

        if self.window == None:
            self.runescapeStart()
            self.window = self.windowSearch()

        time.sleep(3)
        self.windowCorner = (self.window.get_geometry().x, self.window.get_geometry().y)
        self.windowSize = (self.window.get_geometry().width, self.window.get_geometry().height)

        self.templates = self.templatesLoad()

    #**************************************************************************
    # description
    #   selects a world (326)
    def worldPick(self):
        screen = self.screenGet()
        gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
        #reduces the color range to highlight button areas
        _, thrash = cv2.threshold(gray, 50, 150, cv2.THRESH_BINARY_INV)
        buttons = self.buttonsFind(thrash, 3000, 5000)

        worldButton = None
        leftmost = 10000
        for button in buttons:
            if button['center'][0] < leftmost:
                worldButton = button
                leftmost = button['center'][0]
        self.absoluteClick(worldButton['center'], 'left')
        time.sleep(1)

        #next find only the free (white) worlds
        screen = self.screenGet()
        freeMask = cv2.inRange(screen, np.array((150, 150, 150)), np.array((220, 220, 220)))
        freeWorlds = cv2.bitwise_not(freeMask)
        freeWorldButtons = self.buttonsFind(freeWorlds, 50, 60)

        choice = freeWorldButtons[0]#random.choice(freeWorldButtons)
        self.absoluteClick(choice['center'], 'left')
        time.sleep(1)

    #**************************************************************************
    # description
    #   presses the login buttons and types in the username and password
    def login(self, username, password):
        screen = self.screenGet()
        existingUserButton = self.imageMatch(screen, self.templates['existingUserButton'])

        self.absoluteClick(existingUserButton['center'], 'left')
        time.sleep(1)
        self.keyboard.type(username)
        time.sleep(0.5)
        self.keyboard.tab()
        time.sleep(1.1)
        self.keyboard.type(password)
        time.sleep(0.8)
        self.keyboard.enter()
        time.sleep(17)
        #there is another 'play button' after in pretty much the same location
        playButton = (existingUserButton['center'][0], existingUserButton['center'][1] + 20)
        self.absoluteClick(playButton, 'left')
        time.sleep(1)

        #also need to open the inventory
        inventory = self.imageMatch(self.screenGet(), self.templates['inventory'])
        self.absoluteClick(inventory['center'], 'left')
        time.sleep(1)

        #force screen to be topdown view
        self.topViewSet()

    #**************************************************************************
    # description
    #   finds all of the buttons on the screen
    def buttonsFind(self, screen, buttonLower, buttonLarger):
        contours, _ = cv2.findContours(screen, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        buttons = []
        for next in contours:
            area = cv2.contourArea(next)
            #this is to filter out some of the random boxes found
            if area > buttonLower and area < buttonLarger:
                x, y, w, h = cv2.boundingRect(next)
                centerX = x + (w // 2)
                centerY = y + (h // 2)
                buttons.append({'area': area, 'center': (centerX, centerY), 'size': (w, h)})

        return buttons

    #**************************************************************************
    # description
    #   holds down the up button to get a top view
    def topViewSet(self):
        self.keyboard.hold('up')
        time.sleep(2)
        self.keyboard.release('up')

    #**************************************************************************
    # description
    #   searches the x11 space for a window that kinda looks like runescape
    #   make sure there are no other windows open or this could pick the wrong one
    def windowSearch(self):
        window = None

        root = self.display.screen().root
        children = root.query_tree().children
        for win in children:
            try:
                winName = win.get_wm_name()
                attrs = win.get_attributes()

                #either Jagex or jagexappletviewer
                if 'None' in str(winName) and attrs.map_state == Xlib.X.IsViewable:
                    corner = (win.get_geometry().x, win.get_geometry().y)
                    #might help find it. Random windows are < 0
                    size = (win.get_geometry().width, win.get_geometry().height)
                    if corner[0] > 10 and corner[1] > 10:
                        window = win
                        return window

            except Xlib.error.BadWindow:
                print("got badWindow error")

        return window

    #**************************************************************************
    # description
    #   starts the runscape snap in the background. Waits 5 seconds for it to load
    def runescapeStart(self):
        self.runescapeProcess = subprocess.Popen(['snap', 'run', 'runescape.osrs'])
        time.sleep(5)

    #**************************************************************************
    # description
    #   returns a pair x,y coordinate of the window corner
    #   this assumes that the window will not be moved
    def cornerGet(self):
        return self.windowCorner

    #**************************************************************************
    # description
    #   returns the size of the runescape window
    #   this assumes that the window will not be moved
    def sizeGet(self):
        return self.windowSize

    #**************************************************************************
    # description
    #   returns the entire runescape window
    def screenGet(self):
        corner = self.cornerGet()
        size = self.sizeGet()
        img = np.array(ImageGrab.grab())[corner[1]:corner[1]+size[1], corner[0]:corner[0]+size[0]]
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    #**************************************************************************
    # description
    #   returns only the play area. No inventory or chat screen
    def playAreaGet(self):
        corner = self.cornerGet()
        size = self.sizeGet()
        img = np.array(ImageGrab.grab())[corner[1]:corner[1]+size[1], corner[0]:corner[0]+size[0]]
        img = img[25:505, 25:615]
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    #**************************************************************************
    # description
    #   returns only the inventory. No play area or chat screen
    def inventoryAreaGet(self):
        corner = self.cornerGet()
        size = self.sizeGet()
        img = np.array(ImageGrab.grab())[corner[1]:corner[1]+size[1], corner[0]:corner[0]+size[0]]
        img = img[330:-85, 621:-9]
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    #**************************************************************************
    # description
    #   returns only the tabs in the bottom corner. No play area, chat screen or inventory
    def tabsAreaGet(self):
        corner = self.cornerGet()
        size = self.sizeGet()
        img = np.array(ImageGrab.grab())[corner[1]:corner[1]+size[1], corner[0]:corner[0]+size[0]]
        return img[596:-5, 585:-2]

    #**************************************************************************
    # description
    #   loads all of the templates available for the bot to find
    def templatesLoad(self):
        templates = {}

        templates['existingUserButton'] = cv2.imread('templates/existingUserButton.png', 0)
        templates['attackStyle'] = cv2.imread('templates/attackStyle.png', 0)
        templates['emojis'] = cv2.imread('templates/emojis.png', 0)
        templates['emotes'] = cv2.imread('templates/emotes.png', 0)
        templates['equipment'] = cv2.imread('templates/equipment.png', 0)
        templates['friends'] = cv2.imread('templates/friends.png', 0)
        templates['inventory'] = cv2.imread('templates/inventory.png', 0)
        templates['levels'] = cv2.imread('templates/levels.png', 0)
        templates['memberSettings'] = cv2.imread('templates/memberSettings.png', 0)
        templates['prayers'] = cv2.imread('templates/prayers.png', 0)
        templates['quests'] = cv2.imread('templates/quests.png', 0)
        templates['settings'] = cv2.imread('templates/settings.png', 0)
        templates['songs'] = cv2.imread('templates/songs.png', 0)
        templates['spells'] = cv2.imread('templates/spells.png', 0)

        return templates

    #**************************************************************************
    # description
    #   searches for a button using matchTemplate and returns location of button
    # parameters
    #   background
    #       type        - np.array
    #       description - background to search for template button
    #   template
    #       type        - np.array
    #       description - template button to match in the background
    # returns
    #   dictionary of center (x,y) and size (width, height)
    def imageMatch(self, background, template):
        grayBackground = cv2.cvtColor(background, cv2.COLOR_BGR2GRAY)
        result = cv2.matchTemplate(grayBackground, template, cv2.TM_SQDIFF)
        min, max, minLoc, maxLoc = cv2.minMaxLoc(result)
        x, y = minLoc
        height, width = template.shape[::]

        matched = {'center': (x + (width // 2), y + (height // 2)), 'size': (width, height)}

        return matched

    #**************************************************************************
    # description
    #   utilizes the HumanMouse to click somewhere on the screen. Assumes relative coordinates
    # parameters
    #   location
    #       type        - pair of x,y
    #       description - relitive coordinates on the window to click
    #   button
    #       type        - string
    #       description - 'left', 'right', 'middle' buttons to click after moving
    def absoluteClick(self, location, button):
        corner = self.cornerGet()
        #offset is needed, otherwise it clicks on the corner of the object
        location = (int(location[0] + corner[0]), int(location[1] + corner[1]))
        self.mouse.click(location, button)

    #**************************************************************************
    # description
    #   utilizes the HumanMouse to click somewhere on the screen. Assumes scaled down coordinates
    # parameters
    #   location
    #       type        - pair of x,y floats, range [0-1]
    #       description - relitive coordinates on the window to click
    #   button
    #       type        - string
    #       description - 'left', 'right', 'middle' buttons to click after moving
    def click(self, location, button):
        size = self.sizeGet()
        location = ((location[0] * size[0]), (location[1] * size[1]))
        self.absoluteClick(location, button)

    #**************************************************************************
    # description
    #   does not use the HumanMouse. Just goes straight to the location and clicks
    # parameters
    #   location
    #       type        - pair of x,y floats, range [0-1]
    #       description - relitive coordinates on the window to click
    #   button
    #       type        - string
    #       description - 'left', 'right', 'middle' buttons to click after moving
    def straightClick(self, location, button, duration = 0.2):
        corner = self.cornerGet()
        size = self.sizeGet()
        #offset is needed, otherwise it clicks on the corner of the object
        #offset = 20
        location = (location[0] + corner[0], location[1] + corner[1])
        self.mouse.straightClick(location, button, duration)
