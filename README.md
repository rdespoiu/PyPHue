# Archived on 2 February 2022
I created this repository when I was in college and have not had the time to maintain it, so I am archiving it today. I'm glad some people managed to get a little use out of it! Please don't hesitate to reach out with any questions/concerns at roberto.despoiu@gmail.com

# PyPHue
![Alt text](https://github.com/rdespoiu/PyPHue/blob/master/pyphue.png?raw=true)

Official Hue API Documentation: https://www.developers.meethue.com/

### Overview
PyPHue is a simple Python library designed to make interfacing with the Phillips Hue API easy. It can be used with Python 2 and 3.

### What can it do?
- Turn lights on/off
- Get and change light brightness
- Get and change light saturation
- Get and change light hue
- More to come? Let me know if you have any ideas!

### Installation
```shell
pip install pyphue
```

### Usage
Import PyPHue into your Python project using:
```python
import pyphue
```
Yup, it's that easy!

Now, let's get started:
The PyPHue constructor takes several arguments:
```python
### PyPHue Constructor ###
def __init__(self, ip = None, user = None, AppName = 'My_Hue_App', DeviceName = 'Default_Device:JohnDoe', wizard = False):
    ...
'''
IP:
    Hue Bridge IP. PyPHue will validate this if used as a parameter. If no IP is set in the constructor,
    PyPHue will attempt to find a bridge on the network.

User:
    Authorized Hue Bridge user. PyPHue will validate this if used as a parameter. If no value is specified,
    PyPHue will create a user (the bridge has a button that must be pressed first, or PyPHue will throw an error)

AppName:
    Name of the application. This is used by the Hue API to create a user. While the default value is acceptable,
    developers should specify an AppName per the Hue API guidelines.

DeviceName:
    Type of device followed by the owner. Ex. 'iPhone:JohnDoe'. This is also used by the Hue API to create a user,
    and per the API guidelines, developers should choose something unique.

Wizard:
    This is for debugging and playing with PyPHue and as such, is set to False by default. When wizard is set to
    True, PyPHue will prompt you to press the button on the bridge when creating a user. This should be handled
    by developers in their own applications, but it's here to play around with.
'''
```

Let's use the wizard to get started. In your command line, open Python and enter the following:
```
>>> myHue = pyphue.PyPHue(wizard = True)
```

This will print the response:
```
Press the button on the Hue Bridge to authenticate
Press any key to continue once you have completed this step
```

Once you've pressed the button on your bridge, hit any key.
You should now have a PyPHue object ready for use.
```
>>> myHue = pyphue.PyPHue(wizard = True)
Press the button on the Hue Bridge to authenticate
Press any key to continue once you have completed this step

>>> myHue
<pyphue.PyPHue.PyPHue object at 0x1018fc13f>

>>> myHue.ip
101.101.0.101                               # Your bridge IP

>>> myHue.user
B1SnfUA91k01jd92j012dkfiIA81NJA9Huw18UE2    # The user we created

>>> myHue.lightIDs
['1', '2', '3', '4', '5', '6']              # Array of lights connected to the bridge
```

Now that PyPHue is all set up, let's play with some lights!
```python
myHue.turnOn('1')                           # Turns on the light with id '1'
myHue.setBrightness('1', 255)               # Sets light '1' to max brightness (0 - 255)
myHue.setSaturation('1', 255)               # Sets light '1' to max saturation (0 - 255)
myHue.setHue('1', 45000)                    # Sets light '1' to a blue color   (0 - 65535)
myHue.turnOff('1')                          # Turns off light '1'

myHue.toggle('2')                           # Flips the state of light '2'. (i.e. if off, turns it on and vice versa)
myHue.getOnOff('2')                         # Returns the power state of light '2'      (True/False)
myHue.getBrightness('2')                    # Returns the brightness value of light '2' (0 - 255)
myHue.getSaturation('2')                    # Returns the saturation value of light '2' (0 - 255)
myHue.getHue('2')                           # Returns the hue value of light '2'        (0 - 65535)
```

### Advanced Details

##### Bridge IP Address
PyPHue finds the IP of the bridge on the network by sending a GET request to the Phillips Hue UPnP page
https://www.meethue.com/api/nupnp
```python
'''
    This is the method used by PyPHue to find the bridge IP address if none is specified in the constructor.
    It sends a GET request to the UPnP above and attempts to read the 'internalipaddress' key in the response's
    JSON. If this fails, an IPError is raised stating that the bridge IP cannot be resolved.
'''

def getBridgeIP(self):
    try:
        return self.get(self.HUE_NUPNP)['json'][0]['internalipaddress']
    except:
        raise IPError('Could not resolve Hue Bridge IP address. Please ensure your bridge is connected')
```
```python
'''
    If an IP address is specified in the PyPHue constructor, it is validated using the validateIP method.
    PyPHue attempts to send a GET request to the specified IP, and if an 'ok' key is not returned in the
    response, it signifies that the specified IP was invalid and raises an IPError.
'''

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
```



##### Users
PyPHue attempts to create a user if none is specified in the constructor.
```python
'''
    If no user is specified in the constructor, PyPHue will attempt to create a user by sending a POST
    request to the Hue API. If it is successful, PyPHue returns the 'username' key from the response.
    If not, a KeyError will be caught and a BridgeError will be raised, indicating that the button on
    the bridge needs to be pressed.
'''

def createUser(self):
    # Wizard code omitted
    response = self.post(
                    self.url(self.ip, 'api'),
                    {'devicetype': '{}#{}'.format(self.AppName, self.DeviceName)}
                )
    try:
        return response['json'][0]['success']['username']
    except KeyError:
        raise BridgeError('You must press the button on the Hue Bridge...etc...')
```
```python
'''
    If a user is specified in the constructor, PyPHue will attempt to validate the user.
    If the user does not exist in the bridge's list of authorized users, a UserError is raised.
'''
def validateUser(self, user):
    response = self.get(self.url(self.ip, 'api', user))

    if not (type(response['json']) == type(dict()) and response['json'].get('config')):
        raise UserError('Unauthorized user')

    return user
```

### Contact
Thanks for checking out PyPHue! If you need to get in touch, or have any questions/comments/concerns, feel free to email me.
roberto.despoiu@gmail.com
