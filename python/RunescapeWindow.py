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
        options = webdriver.ChromeOptions()
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36')
        #options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4324.104 Safari/537.36')
        options.add_argument('start-maximized')
        options.add_argument('window-size=1920,1080')
        options.add_argument('disable-infobars')
        options.add_argument('dom.webdriver.enabled", False')
        caps = webdriver.DesiredCapabilities.CHROME.copy()
        caps['platform'] = 'Windows NT 10'
        caps['version'] = '74.0.3729.169'
        caps['binary_location'] = 'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe'
        #options.add_user_profile_preference("dom.webdriver.enabled", False)
        self.driver = webdriver.Chrome(executable_path='/tmp/work/chromeDriver/chromedriver', options=options, desired_capabilities=caps)
        self.driver.execute_script("Object.defineProperty(screen, 'height', {value: 1080, configurable: true, writeable: true});");
        self.driver.execute_script("Object.defineProperty(screen, 'width', {value: 1920, configurable: true, writeable: true});");
        self.driver.execute_script("Object.defineProperty(screen, 'availWidth', {value: 1920, configurable: true, writeable: true});");
        self.driver.execute_script("Object.defineProperty(screen, 'availHeight', {value: 1080, configurable: true, writeable: true});");
        #self.driver.define_property('webdriver=false')
        pos = self.driver.get_window_position()
        self.windowCornerX = int(pos['x'])
        self.windowCornerY = int(pos['y'])
        self.driver.get("https://www.oldschool.runescape.com")
        time.sleep(0.6)
        loginLink = self.findElementByText('Log in')
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
