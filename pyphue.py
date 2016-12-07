import requests
import json
import time
from pyphueexceptions import *


class PyPHue:
    AppName = str()
    DeviceName = str()
    wizard = bool()
    user = str()
    ip = str()
    baseURL = str()
    HUE_NUPNP = 'https://www.meethue.com/api/nupnp'

    # Dictionary of friendly light names
    friendlyLights = dict()

    # List of light IDs
    lightIDs = list()

    def __init__(self, ip = None, user = None, AppName = 'My_Hue_App', DeviceName = 'Default_Device JohnDoe', wizard = False):
        self.AppName = AppName
        self.DeviceName = DeviceName
        self.wizard = wizard

        self.ip = self.validateIP(ip) if ip else self.getBridgeIP()
        self.user = self.validateUser(user) if user else self.createUser()
        self.baseURL = 'http://{}/api/{}'.format(self.ip, self.user)

        self.mapLights()

    def mapLights(self):
        lights = self.get('{}/lights/'.format(self.baseURL))
        self.lightIDs = [lightID for lightID in lights['json'].keys()]

    def assignLightName(self, lightID, name):
        self.friendlyLights[name] = lightID

    def lightInfo(self, lightID):
        response = self.get('{}/lights/{}/'.format(self.baseURL, lightID))
        return response


    #############################
    # TURNING LIGHTS ON AND OFF #
    #############################

    def toggle(self, lightID):
        state = self.lightInfo(lightID)['json']['state']['on']
        response = self.put('{}/lights/{}/state/'.format(self.baseURL, lightID), {'on': not state})
        return response

    def turnOff(self, lightID):
        response = self.put('{}/lights/{}/state/'.format(self.baseURL, lightID), {'on': False})
        return response

    def turnOn(self, lightID):
        response = self.put('{}/lights/{}/state/'.format(self.baseURL, lightID), {'on': True})
        return response


    #############################
    # HUE/BRIGHTNESS/SATURATION #
    #############################

    def getBrightness(self, lightID):
        response = self.get('{}/lights/{}/'.format(self.baseURL, lightID))
        return response['json']['state']['bri']

    # Max: 254
    def setBrightness(self, lightID, brightness):
        response = self.put('{}/lights/{}/state/'.format(self.baseURL, lightID), {'bri': brightness})
        return response

    def getSaturation(self,lightID):
        response = self.get('{}/lights/{}/'.format(self.baseURL, lightID))
        return response['json']['state']['sat']

    # Max: 254
    def setSaturation(self, lightID, saturation):
        response = self.put('{}/lights/{}/state/'.format(self.baseURL, lightID), {'sat': saturation})
        return response

    def getHue(self, lightID):
        response = self.get('{}/lights/{}/'.format(self.baseURL, lightID))
        return response['json']['state']['hue']

    # Max: 65535
    def setHue(self, lightID, hue):
        response = self.put('{}/lights/{}/state/'.format(self.baseURL, lightID), {'hue': hue})
        return response


    ################
    # HTTP METHODS #
    ################

    def get(self, url):
        response = requests.get(url, timeout = 10)
        return self.responseData(response)

    def put(self, url, payload):
        response = requests.put(url, data = json.dumps(payload))
        return self.responseData(response)

    def post(self, url, payload):
        response = requests.post(url, data = json.dumps(payload))
        return self.responseData(response)

    def responseData(self, response):
        data = {'status_code': response.status_code, 'ok': response.ok}
        if response.ok:
            data['json'] = response.json()
        return data


    #############
    # HUE SETUP #
    #############

    def getBridgeIP(self):
        try:
            return self.get(self.HUE_NUPNP)['json'][0]['internalipaddress']
        except:
            raise IPError('Could not resolve Hue Bridge IP address. Please ensure your bridge is connected')

    def validateIP(self, ip):
        try:
            data = requests.get('http://{}/api/'.format(self.ip))
            if not data['ok']:
                raise IPError('Invalid Hue Bridge IP address')
        except (requests.exceptions.ConnectionError,
                requests.exceptions.MissingSchema,
                requests.exceptions.ConnectTimeout):
            raise IPError('Invalid Hue Bridge IP address')

    def validateUser(self, user):
        response = self.get('http://{}/api/{}'.format(self.ip, user))

        if not (type(response['json']) == type(dict()) and response['json'].get('config')):
            raise UserError('Unauthorized user')

        return user

    def createUser(self):
        if self.wizard:
            print 'Press the button on the Hue Bridge to authenticate'
            print 'Press any key to continue once you have completed this step'
            raw_input()

        response = self.post('http://{}/api/'.format(self.ip), {'devicetype': '{}#{}'.format(self.AppName, self.DeviceName)})

        try:
            return response['json'][0]['success']['username']
        except KeyError:
            raise BridgeError('You must press the button on the Hue Bridge. If you have already done this, ensure your bridge is online and you are both on the same network.')
