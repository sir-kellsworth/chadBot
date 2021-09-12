import pynput.keyboard
import time

class Keyboard:
    #**************************************************************************
    # description
    #   constructor
    def __init__(self):
        self.keyboard = pynput.keyboard.Controller()

    #**************************************************************************
    # description
    #   types a string with some delays between each keystroke
    # parameters
    #   string
    #       type        - string
    #       description - word or sentance to type. literals only
    def type(self, string):
        for next in string:
            self.keyboard.press(next)
            time.sleep(0.07)
            self.keyboard.release(next)
            time.sleep(0.06)

    #**************************************************************************
    # description
    #   hits the tab button
    def tab(self):
        self.keyboard.press(pynput.keyboard.Key.tab)
        time.sleep(0.1)
        self.keyboard.release(pynput.keyboard.Key.tab)
        time.sleep(0.08)

    #**************************************************************************
    # description
    #  hits the enter key
    def enter(self):
        self.keyboard.press(pynput.keyboard.Key.enter)
        time.sleep(0.1)
        self.keyboard.release(pynput.keyboard.Key.enter)
        time.sleep(0.08)

    #**************************************************************************
    # description
    #  holds a key
    # parameters
    #   key
    #       type        - string
    #       description - can be a special button like 'up', or 'down'. Otherwise assumes a key like 'g'
    def hold(self, key):
        if key == 'up':
            self.keyboard.press(pynput.keyboard.Key.up)
        elif key == 'down':
            self.keyboard.press(pynput.keyboard.Key.down)
        else:
            self.keyboard.press(key)

    #**************************************************************************
    # description
    #  releases a key
    # parameters
    #   key
    #       type        - string
    #       description - can be a special button like 'up', or 'down'. Otherwise assumes a key like 'g'
    def release(self, key):
        if key == 'up':
            self.keyboard.release(pynput.keyboard.Key.up)
        elif key == 'down':
            self.keyboard.release(pynput.keyboard.Key.down)
        else:
            self.keyboard.release(key)
