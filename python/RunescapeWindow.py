import Xlib
import Xlib.display
import Xlib.X
import time
import subprocess

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

            except Xlib.error.BadWindow:
                print("got badWindow error")

        return window

    #**************************************************************************
    def runescapeStart(self):
        self.runescapeProcess = subprocess.Popen(['snap', 'run', 'runescape.osrs'])
        time.sleep(5)

if __name__ == "__main__":
    testWindow = RunescapeWindow()
    testWindow.login("chadsbutt@gmail.com", "McDemShoulders")
