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

#signal handler is for aws to stop a bot
def signalHandle(self, signal, frame):
    running = False

running = True
signal.signal(signal.SIGINT, signalHandle)

profile = Profile.Profile(sys.argv[1])
window = RunescapeWindow.RunescapeWindow()
window.worldPick()
window.login(profile.emailGet(), profile.passwordGet())
window.topViewSet()

bot = Miner(profile, window, debug=True)

while running:
    bot.step()

window.logout()
window.kill()
