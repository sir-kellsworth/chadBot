import threading
import cv2
import numpy as np
import time
import pytesseract as tess
from PIL import Image

class RandomEventDetection:
    def __init__(self, window, callback):
        self.window = window
        self.callback = callback
        self.debug = True
        self.textRange = ([0, 100, 100], [30, 255, 256])
        self.running = True
        self.backgroundThread = threading.Thread(target=self.run)
        self.backgroundThread.start()

    def __del__(self):
        self.running = False
        self.backgroundThread.join()

    def run(self):
        while self.running:
            playArea = self.window.playAreaGet()
            textMask = cv2.inRange(playArea, np.array(self.textRange[0]), np.array(self.textRange[1]))
            kernel = np.ones((10, 10), np.uint8)
            closing = cv2.morphologyEx(textMask.copy(), cv2.MORPH_CLOSE, kernel)
            _, closing = cv2.threshold(closing, 0, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(closing, 1, 2)
            textAreas = []
            for next in contours:
                x, y, w, h = cv2.boundingRect(next)

                #gets number of mines found
                area = cv2.contourArea(next)
                if area > 60:
                    if self.debug:
                        cv2.imshow('texts', textMask[y-5:y+h+5, x-5:x+w+5])
                        cv2.waitKey(30)
                    textImage = Image.fromarray(textMask[y-5:y+h+5, x-5:x+w+5])
                    interpretedText = tess.image_to_string(textImage).strip()
                    if interpretedText != "":
                        print(interpretedText)
                        if 'chadsButts' in interpretedText:
                            print('found actual random event')
                            self.callback(textAreas[0])


            time.sleep(0.3)
