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
    def worldPick(self):
        corner = self.cornerGet()
        worldPickButton = (87, 514)
        world326 = (235, 94)

        worldPickButton = (corner[0] + worldPickButton[0], corner[1] + worldPickButton[1])
        world326 = (corner[0] + world326[0], corner[1] + world326[1])

        self.mouse.click(worldPickButton, 'left')
        time.sleep(2)
        self.mouse.click(world326, 'left')
        time.sleep(2)

    #**************************************************************************
    def login(self, username, password):
        existingUserButtonXOffset = 494
        existingUserButtonYOffset = 340
        loginXOffset = 338
        loginYOffset = 368
        existingUserButtonX = self.windowCorner[0] + existingUserButtonXOffset
        existingUserButtonY = self.windowCorner[1] + existingUserButtonYOffset
        loginButton = (self.windowCorner[0] + loginXOffset, self.windowCorner[1] + loginYOffset)

        print("corner: " + str(self.windowCorner))
        print("expected:" + str((existingUserButtonX, existingUserButtonY)))

        self.mouse.click((existingUserButtonX, existingUserButtonY), 'left')
        time.sleep(1)
        self.keyboard.type(username)
        time.sleep(0.5)
        self.keyboard.tab()
        time.sleep(1.1)
        self.keyboard.type(password)
        time.sleep(0.8)
        self.keyboard.enter()
        time.sleep(3)

    #**************************************************************************
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
    def runescapeStart(self):
        self.runescapeProcess = subprocess.Popen(['snap', 'run', 'runescape.osrs'])
        time.sleep(5)

    #**************************************************************************
    def cornerGet(self):
        return (self.window.get_geometry().x, self.window.get_geometry().y)

    #**************************************************************************
    def sizeGet(self):
        return (self.window.get_geometry().width, self.window.get_geometry().height)

    #**************************************************************************
    def playAreaGet(self):
        corner = self.cornerGet()
        size = self.sizeGet()
        img = np.array(ImageGrab.grab())[corner[1]:corner[1]+size[1], corner[0]:corner[0]+size[0]]
        img = img[25:505, 25:615]
        return cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    #**************************************************************************
    def click(self, location, button):
        corner = self.cornerGet()
        location = (location[0] + corner[0] + 20, location[1] + corner[1] + 20)
        self.mouse.click(location, button)

if __name__ == "__main__":
    testWindow = RunescapeWindow()
    testWindow.login("chadsbutt@gmail.com", "McDemShoulders")
