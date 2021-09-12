install:
  to install run ./setup.py
  it will first install all packages using apt
  then install all packages from python/requirements.txt
  then install the runscape snap

run:
  right now it only supports the default screen size.
    making it bigger or smaller will cause issues
  to run the bot:
    python3 python/main.py config/miner.conf
  all other helpful scripts are in python/scripts/
    colorSampler.py       -   prints RGB values of pixel under cursor
    loginTest.py          -   shows login with world select
    mouseLocationPrint.py -   prints mouse location relative to window corner
    windowCheck.py        -   shows what the bot sees
    pathRecord.py         -   records mouse and keyboard interactions and saves to file for bot to use

config:
  expected values:
    [paths]
    nameOfPath = fileName

    [Idle]
    messages = list of idle messages
    speakChance = [0-1] chance to speak every 10 minutes

    [Mining]
    target = mine to target (this is the value that the bot will use to mask the screen)

    [Login]
    username
    password = password to use to login to runescape snap

    [Email]
    firstName
    lastName
    email = email to use to login to runescape snap
    password = password for email account
