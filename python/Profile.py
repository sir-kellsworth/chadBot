import configparser
import os

class Profile:
    #**************************************************************************
    def __init__(self, configFile):
        self.config = configparser.ConfigParser()
        self.config.read(configFile)

    #**************************************************************************
    def emailGet(self):
        return self.config.get('Email', 'email')

    def passwordGet(self):
        return self.config.get('Login', 'password')

    #**************************************************************************
    def idleMessagesGet(self):
        return self.config.get('Idle', 'messages')

    #**************************************************************************
    def idleChanceGet(self):
        return self.config.get('Idle', 'speakChance')

    def pathsGet(self):
        paths = []
        tmp = self.config.items('paths')
        for key, path in tmp:
            paths.append({'PathName': key, 'File': path})

        return paths
