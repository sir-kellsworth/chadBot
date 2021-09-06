from selenium import webdriver
import time
import pyautogui
from Mouse.HumanMouse import HumanMouse

class RunescapeWindow:
    #**************************************************************************
    def __init__(self):
        self.mouse = HumanMouse()
        self.windowScaleX = 2
        self.windowScaleY = 2
        self.elementScaleX = 2
        self.elementScaleY = 12
        self.driver = webdriver.Chrome(executable_path='/tmp/work/chromeDriver/chromedriver')
        self.screenCornerX, self.screenCornerY = self.driver.get_window_position()
        self.driver.get("https://www.oldschool.runescape.com")
        time.sleep(1)
        loginLink = self.driver.findElementByText('Log in')
        self.clickElement(loginLink, 'left')

    #**************************************************************************
    def login(self, loginPair):
        error = self.findElementByText('Access Denied')
        if error != None:
            loginField = self.findElementByText('Username')
            passwordField = self.findElementByText('Password')
            loginField.send_keys(loginPair['username'])
            passwordField.send_keys(loginPair['password'])
        else:
            print("got found. Bailing")
            time.sleep(5)
            self.driver.close()
            exit(1)

    #**************************************************************************
    def logout(self):
        logout = self.findElementByText('logout')
        logout.press()

    #**************************************************************************
    def kill(self):
        self.window.close()

    #**************************************************************************
    def playableWindowGet(self):
        return self.find('mainWindow')

    #**************************************************************************
    def findElementByText(self, label):
        try:
            return self.driver.find_element_by_xpath("//*[contains(text(), '" + label + "')]")
        except Exception as e:
            return None

    #**************************************************************************
    def findElementById(self, id):
        try:
            return self.driver.find_element_by_id(id)
        except Exception as e:
            return None

    #**************************************************************************
    def clickElement(self, element, button):
        location = element.location
        size = element.size
        left = location['x']
        top = location['y']
        centerX = left + (size['width'] // 2)
        centerY = top + (size['height'] // 2)
        positionX = (self.windowCornerX * self.windowScaleX) + (centerX * self.elementScaleX)
        positionY = (self.windowCornerY * self.windowScaleY) + (centerY * self.elementScaleY)
        self.mouse.click((positionX, positionY), button)
