class MouseMoveEvent:
    def __init__(self, timestamp, location):
        self.timestamp = float(timestamp)
        self.location = tuple(location)

class MouseClickEvent:
    def __init__(self, timestamp, location, button, pressed):
        self.timestamp = float(timestamp)
        self.location = tuple(location)
        self.button = button
        self.pressed = pressed

class MouseScrollEvent:
    def __init__(self, timestamp, location, scrollDiff):
        self.timestamp = float(timestamp)
        self.location = tuple(location)
        self.scrollDiff = scrollDiff

class KeyPressedEvent:
    def __init__(self, timestamp, key):
        self.timestamp = float(timestamp)
        self.key = key

class KeyReleasedEvent:
    def __init__(self, timestamp, key):
        self.timestamp = float(timestamp)
        self.key = key
