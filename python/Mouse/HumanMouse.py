import pyautogui
import pytweening
import numpy as np
import random
from Mouse.HumanCurve import HumanCurve

class HumanMouse:
    #**************************************************************************
    def __init__(self, duration=0.015, interval=0.015):
        self.duration = duration
        self.interval = interval

    #**************************************************************************
    def positionGet(self):
        return pyautogui.position()

    #**************************************************************************
    def moveTo(self, toPos):
        fromPos = pyautogui.position()
        curve = HumanCurve(fromPos, toPos)
        for point in curve.points:
            pyautogui.moveTo(point)

    def onlyClick(self, button):
        pyautogui.click(button=button)

    #**************************************************************************
    def click(self, toPos, button):
        fromPos = pyautogui.position()
        curve = HumanCurve(fromPos, toPos)
        for point in curve.points:
            pyautogui.moveTo(point)

        pyautogui.click(button=button)

    #**************************************************************************
    def straightClick(self, toPos, button, duration):
        pyautogui.moveTo(toPos, duration=duration)
        pyautogui.click(button=button)

    #**************************************************************************
    def doubleClick(self, toPos, button):
        fromPos = pyautogui.position()
        curve = HumanCurve(fromPos, toPos)
        for point in curve.points:
            pyautogui.moveTo(point)

        pyautogui.doubleClick(button=button, duration=self.duration, interval=self.interval)
