import pynput.keyboard
import time

class Keyboard:
    def __init__(self):
        self.keyboard = pynput.keyboard.Controller()

    def type(self, string):
        for next in string:
            self.keyboard.press(next)
            time.sleep(0.07)
            self.keyboard.release(next)
            time.sleep(0.06)

    def tab(self):
        self.keyboard.press(pynput.keyboard.Key.tab)
        time.sleep(0.1)
        self.keyboard.release(pynput.keyboard.Key.tab)
        time.sleep(0.08)

    def enter(self):
        self.keyboard.press(pynput.keyboard.Key.enter)
        time.sleep(0.1)
        self.keyboard.release(pynput.keyboard.Key.enter)
        time.sleep(0.08)
