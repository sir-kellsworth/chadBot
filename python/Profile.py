import configparser

class Profile:
    #**************************************************************************
    def __init__(self, configFile):
        self.config = configparser.ConfigParser()
        self.config.read(configFile)

    #**************************************************************************
    def loginGet(self):
        return (self.config.get('Login', 'username'), self.config.get('Login', 'password'))

    #**************************************************************************
    def pathsGet(self):
        return self.config.get('Pathing', 'paths')

    #**************************************************************************
    def idleMessagesGet(self):
        return self.config.get('Idle', 'messages')

    #**************************************************************************
    def idleChanceGet(self):
        return self.config.get('Idle', 'speakChance')
