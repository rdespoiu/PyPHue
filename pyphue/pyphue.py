import sys
import requests
import json


class PyPHue:
    PYTHON_VERSION = sys.version_info.major

    AppName = str()
    DeviceName = str()
    wizard = bool()
    user = str()
    ip = str()
    baseURL = str()
    HUE_NUPNP = 'https://www.meethue.com/api/nupnp'

    # List of light IDs
    lightIDs = list()


    ###############
    # CONSTRUCTOR #
    ###############

    '''
    PyPHue can be initialized without any parameters

        IP:         Hue Bridge IP. PyPHue will validate this if used as a parameter.

        User:       Authorized Hue Bridge user. PyPHue will validate this if used as a parameter.

        AppName:    Name of the application, used for generating a user. Default 'My_Hue_App' if left blank.

        DeviceName: Type of device followed by the owner. Default 'iPhone:JohnDoe' if left blank.

        Wizard:     Mostly for debugging. Set wizard to true for verbose bridge connection.
                    PyPHue will prompt you to press the button on the bridge when creating a user.
    '''

    def __init__(self, ip = None, user = None, AppName = 'My_Hue_App', DeviceName = 'Default_Device:JohnDoe', wizard = False):
        self.AppName = AppName
        self.DeviceName = DeviceName
        self.wizard = wizard

        self.ip = self.validateIP(ip) if ip else self.getBridgeIP()
        self.user = self.validateUser(user) if user else self.createUser()
        self.baseURL = '{}/api/{}'.format(self.ip, self.user)

        self.mapLights()


    ###########################
    # LIGHT STATE CONTROLLERS #
    ###########################

    # Flips the state of specified light
    def toggle(self, lightID):
        state = self.getLight(lightID)['json']['state']['on']
        response = self.putLight(lightID, {'on': not state})
        return response

    # Sets the state of specified light to False (off)
    def turnOff(self, lightID):
        response = self.putLight(lightID, {'on': False})
        return response

    # Sets the state of specified light to True (on)
    def turnOn(self, lightID):
        response = self.putLight(lightID, {'on': True})
        return response


    #########################################
    # HUE/BRIGHTNESS/SATURATION CONTROLLERS #
    #########################################

    # Brightness: 0 - 254
    # Saturation: 0 - 254
    # Hue:        0 - 65535

    # Returns the brightness value of specified light
    def getBrightness(self, lightID):
        response = self.getLight(lightID)
        return response['json']['state']['bri']

    # Sets the brightness value for specified light
    def setBrightness(self, lightID, brightness):
        response = self.putLight(lightID, {'bri': brightness})
        return response

    # Returns the saturation value of specified light
    def getSaturation(self,lightID):
        response = self.getLight(lightID)
        return response['json']['state']['sat']

    # Sets the saturation value for specified light
    def setSaturation(self, lightID, saturation):
        response = self.putLight(lightID, {'sat': saturation})
        return response

    # Returns the hue value of spepcified light
    def getHue(self, lightID):
        response = self.getLight(lightID)
        return response['json']['state']['hue']

    # Sets the hue value for specified light
    def setHue(self, lightID, hue):
        response = self.putLight(lightID, {'hue': hue})
        return response


    ################
    # HTTP METHODS #
    ################

    # GET Request
    def get(self, url):
        response = requests.get(url, timeout = 10)
        return self.responseData(response)

    # PUT Request
    def put(self, url, payload):
        response = requests.put(url, data = json.dumps(payload))
        return self.responseData(response)

    # POST Request
    def post(self, url, payload):
        response = requests.post(url, data = json.dumps(payload))
        return self.responseData(response)


    #############
    # HUE SETUP #
    #############

    # Gets bridge IP using Hue's NUPNP site. Device must be on the same network as the bridge
    def getBridgeIP(self):
        try:
            return self.get(self.HUE_NUPNP)['json'][0]['internalipaddress']
        except:
            raise IPError('Could not resolve Hue Bridge IP address. Please ensure your bridge is connected')

    # If given a brige IP as a constructor parameter, this validates it
    def validateIP(self, ip):
        try:
            data = self.get('http://{}/api/'.format(ip))
            if not data['ok']:
                raise IPError('Invalid Hue Bridge IP address')
        except (requests.exceptions.ConnectionError,
                requests.exceptions.MissingSchema,
                requests.exceptions.ConnectTimeout):
            raise IPError('Invalid Hue Bridge IP address')

        return ip

    # If given a user as a constructor parameter, this validates it
    def validateUser(self, user):
        response = self.get(self.url(self.ip, 'api', user))

        if not (type(response['json']) == type(dict()) and response['json'].get('config')):
            raise UserError('Unauthorized user')

        return user

    # Creates user. If using wizard (verbose mode), PyPHue will wait for user to press bridge button and manually resume the application
    def createUser(self):
        if self.wizard:
            print('Press the button on the Hue Bridge to authenticate')
            print('Press any key to continue once you have completed this step')
            raw_input() if self.PYTHON_VERSION < 3 else input()

        response = self.post(self.url(self.ip, 'api'), {'devicetype': '{}#{}'.format(self.AppName, self.DeviceName)})

        try:
            return response['json'][0]['success']['username']
        except KeyError:
            raise BridgeError('You must press the button on the Hue Bridge. If you have already done this, ensure your bridge is online and you are both on the same network.')


    ###########
    # HELPERS #
    ###########

    # URL constructor
    def url(self, *args):
        return 'http://{}'.format('/'.join(list(args)))

    # Returns URL for specified light ID
    def lightURL(self, lightID, state = False):
        return self.url(self.baseURL, 'lights', lightID) + ('/state' if state else '')

    # PUT a payload at specified light ID
    def putLight(self, lightID, payload):
        return self.put(self.lightURL(lightID, True), payload)

    # GET light information
    def getLight(self, lightID):
        return self.get(self.lightURL(lightID))

    # Maps lights to local lightIDs array
    def mapLights(self):
        lights = self.get('http://{}/lights/'.format(self.baseURL))
        self.lightIDs = [lightID for lightID in lights['json'].keys()]

    # Takes HTTP request response and returns pertinent information in a dict
    def responseData(self, response):
        data = {'status_code': response.status_code, 'ok': response.ok}
        if response.ok:
            data['json'] = response.json()
        return data


#####################
# CUSTOM EXCEPTIONS #
#####################

class IPError(Exception):
    ''' Raise when the Hue Bridge IP address cannot be resolved '''

class UserError(Exception):
    ''' Raise when PyPHue is initialized with an invalid user '''

class BridgeError(Exception):
    ''' Raise when the button on the Hue Bridge has not been pressed '''


####################################
# SETUP (FOR USING AS PYPI MODULE) #
####################################

def setup(ip = None, user = None, AppName = 'My_Hue_App', DeviceName = 'Default_Device:JohnDoe', wizard = False):
    return PyPHue(ip, user, AppName, DeviceName, wizard)
