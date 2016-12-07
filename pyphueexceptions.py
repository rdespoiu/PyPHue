class IPError(Exception):
    ''' Raise when the Hue Bridge IP address cannot be resolved '''

class UserError(Exception):
    ''' Raise when PyPHue is initialized with an invalid user '''

class BridgeError(Exception):
    ''' Raise when the button on the Hue Bridge has not been pressed '''
