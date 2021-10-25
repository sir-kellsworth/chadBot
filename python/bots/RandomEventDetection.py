import threading
import cv2
import numpy as np
import time

class RandomEventDetection:
    def __init__(self, window, callback):
        self.window = window
        self.callback = callback
        self.debug = True
        self.textRange = ([0, 170, 170], [20, 265, 266])
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
            contours, _ = cv2.findContours(closing, 1, 2)
            textAreas = []
            for next in contours:
                x, y, w, h = cv2.boundingRect(next)
                #good for debuging. Draws rectagles over the mines
                if self.debug:
                    cv2.rectangle(playArea, (x, y), (x+w, y+h), (255, 255, 255), -1)
                    cv2.imshow('texts', playArea)

                #gets number of mines found
                area = cv2.contourArea(next)
                #500 just picked. Might need to adjust this
                if area > 30:
                    M = cv2.moments(next)
                    cx = int(M['m10'] / M['m00'])
                    cy = int(M['m01'] / M['m00'])
                    textAreas.append({'area': area, 'location': (cx, cy)})

            if len(textAreas) > 0:
                print("found: " + str(len(textAreas)))
                self.callback(location)

            time.sleep(1)
