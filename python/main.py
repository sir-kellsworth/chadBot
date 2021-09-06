#!/usr/bin/python

import bots
import Profile
import RunescapeWindow
import signal
import sys

if len(sys.argv) != 2:
    print("usage: ./main.py profile.conf")
    exit(1)

def signalHandle(self, signal, frame):
    running = False

running = True
signal.signal(signal.SIGINT, signalHandle)

profile = Profile.Profile(sys.argv[1])
window = RunescapeWindow.RunescapeWindow()
window.login(profile.loginGet())
bot = bots.Minner(profile.configGet(), window)

while running:
    bot.step()

window.logout()
window.kill()
