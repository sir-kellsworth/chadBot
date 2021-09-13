import Xlib
import Xlib.display
import Xlib.X
import time
import subprocess
import numpy as np
import cv2
from PIL import ImageGrab

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

        self.windowCorner = (self.window.get_geometry().x, self.window.get_geometry().y)
        self.windowSize = (self.window.get_geometry().width, self.window.get_geometry().height)

    #**************************************************************************
    # description
    #   selects a world (326)
    def worldPick(self):
        size = self.sizeGet()
        worldPickButton = (87, 500)
        worldPickButtonScaled = (0.10622710622710622, 0.7396449704142012)#(worldPickButton[0] / size[0], worldPickButton[1] / size[1])
        print("**********")
        print("world pick button scaled: " + str(worldPickButtonScaled))
        print("**********")
        world326Button = (235, 80)
        world326ButtonScaled = (0.2869352869352869, 0.11834319526627218)#(world326Button[0] / size[0], world326Button[1] / size[1])
        print("**********")
        print("world pick button scaled: " + str(world326ButtonScaled))
        print("**********")

        self.click(worldPickButtonScaled, 'left')
        time.sleep(1)
        self.click(world326ButtonScaled, 'left')
        time.sleep(1)

    #**************************************************************************
    # description
    #   presses the login buttons and types in the username and password
    def login(self, username, password):
        size = self.sizeGet()
        existingUserButton = (494, 310)
        existingUserScaled = (existingUserButton[0] / size[0], existingUserButton[1] / size[1])
        print("**********")
        print("existing user scaled: " + str(existingUserScaled))
        print("**********")
        inventoryButton = (700, 592)
        inventoryButtonScaled = (inventoryButton[0] / size[0], inventoryButton[1] / size[1])
        print("**********")
        print("inventory button scaled: " + str(inventoryButtonScaled))
        print("**********")

        self.click(existingUserScaled, 'left')
        time.sleep(1)
        self.keyboard.type(username)
        time.sleep(0.5)
        self.keyboard.tab()
        time.sleep(1.1)
        self.keyboard.type(password)
        time.sleep(0.8)
        self.keyboard.enter()
        time.sleep(5)
        #there is another 'play button' after in pretty much the same location
        self.click(existingUserScaled, 'left')
        time.sleep(2)

        #also need to open the inventory
        self.click(inventoryButtonScaled, 'left')
        time.sleep(1)

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
                    print(winName)
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
    def cornerGet(self):
        return (self.window.get_geometry().x, self.window.get_geometry().y)

    #**************************************************************************
    # description
    #   returns the size of the runescape window
    def sizeGet(self):
        return (self.window.get_geometry().width, self.window.get_geometry().height)

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
        offset = 20
        location = (int(location[0] + corner[0] + offset), int(location[1] + corner[1] + offset))
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
    def straightClick(self, location, button):
        corner = self.cornerGet()
        size = self.sizeGet()
        #offset is needed, otherwise it clicks on the corner of the object
        offset = 20
        location = (location[0] + corner[0] + offset, location[1] + corner[1] + offset)
        self.mouse.straightClick(location, button)
