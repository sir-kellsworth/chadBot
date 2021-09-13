import configparser
import os

class Profile:
    #**************************************************************************
    # description
    #   constrcutor
    # parameters
    #   configFile
    #       type        - string
    #       description - file location to load config file from
    def __init__(self, configFile):
        self.config = configparser.ConfigParser()
        self.config.read(configFile)

    #**************************************************************************
    # description
    #   returns the email from the config file
    def emailGet(self):
        return self.config.get('Email', 'email')

    #**************************************************************************
    # description
    #  returns the password for the runescape account
    def passwordGet(self):
        return self.config.get('Login', 'password')

    #**************************************************************************
    # description
    #  returns a list of idel messages
    def idleMessagesGet(self):
        return self.config.get('Idle', 'messages')

    #**************************************************************************
    # description
    #  returns the idle chance as a float
    def idleChanceGet(self):
        return float(self.config.get('Idle', 'speakChance'))

    #**************************************************************************
    # description
    #  returns a list of premade paths and their names
    def pathsGet(self):
        paths = []
        tmp = self.config.items('paths')
        for key, path in tmp:
            paths.append({'PathName': key, 'File': path})

        return paths

    def targetGet(self):
        return self.config.get('Mining', 'target')
