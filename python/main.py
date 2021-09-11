#!/usr/bin/python

from bots.Miner import Miner
import Profile
import RunescapeWindow
import signal
import sys
import time

if len(sys.argv) != 2:
    print("usage: ./main.py profile.conf")
    exit(1)

def signalHandle(self, signal, frame):
    running = False

running = True
signal.signal(signal.SIGINT, signalHandle)

profile = Profile.Profile(sys.argv[1])
window = RunescapeWindow.RunescapeWindow()
window.worldPick()
window.login(profile.emailGet(), profile.passwordGet())

#sleeps a little to wait for runescape to load
time.sleep(10)

bot = Miner(profile, window)

while running:
    bot.stepTest()

#window.logout()
#window.kill()
