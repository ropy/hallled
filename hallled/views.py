import logging
import json

from pyramid.view import view_config
from hallled.serial_command.SerialCommand import SerialCommand


ser = SerialCommand()
log = logging.getLogger(__name__)


@view_config(route_name='home', renderer='templates/hallled.pt')
def my_view(request):
    """
    The home view.

    :param request:
    :return: dict with variables to be rendered
    """
    return {'project': 'HallLed'}


@view_config(route_name='api_led_hslm', renderer='json')
def api_led_hsla(request):
    """

    :param request:
    :return:
    """

    rememberRequest(request)
    inHue = request.matchdict['hue']
    inSat = request.matchdict['saturation']
    inLig = request.matchdict['lightning']
    inModulo = request.matchdict['modulo']
    log.debug("hue: %s, saturation: %s, lightning: %s, modulo: %s", inHue, inSat, inLig, inModulo)
    hue = translate(int(request.matchdict['hue']), 0, 360, 0, 254)
    saturation = translate(float(request.matchdict['saturation']), 0, 1, 0, 254)
    lightning = translate(float(request.matchdict['lightning']), 0, 1, 0, 254)
    modulo = int(inModulo)
    log.debug("hue: %i, saturation: %i, lightning: %i, modulo: %i", hue, saturation, lightning, modulo)
    r = ser.sendHSLM(hue, saturation, lightning, modulo)
    response = ""
    if hasattr(r, 'decode'):
        response = r.decode()
    return dict(arduino=response)

@view_config(route_name='api_led_rgbm', renderer='json')
def api_led_rgb(request):
    rememberRequest(request)
    inRed = request.matchdict['red']
    inGreen = request.matchdict['green']
    inBlue = request.matchdict['blue']
    inModulo = request.matchdict['modulo']

    log.debug("red: %s, green: %s, blue: %s, modulo: %s", inRed, inGreen, inBlue, inModulo)
    red = int(inRed)
    green = int(inGreen)
    blue = int(inBlue)
    modulo = int(inModulo)

    # build the 8 byte command with pre and postfix
    # command = ser.SERIAL_START + 'r' + red + green + blue + modulo + '000' + ser.SERIAL_END
    # response= ser.send(command)
    r = ser.sendRGBM(red, green, blue, modulo)

    return dict(arduino=r)

@view_config(route_name='api_info', renderer='json')
def api_info(request):
    data = ""
    with open('hallled/data/request.txt', 'r') as f:
        data = json.load(f)

    # define default rgbm values
    if not data:
        data = {'r':30, 'g':30, 'b':20, 'm':10}

    return data

@view_config(route_name='api_serialcommand', renderer='json')
def api_raw(request):
    command = request.matchdict['command']
    response = ser.send(command)
    return dict(arduino=response)

def rememberRequest(request):
    path = request.current_route_path()
    log.debug(path)
    path = path[9:]
    action = path[:path.find('/')]
    path = path[path.find('/')+1:]
    data = dict()
    for i in range(0,len(action)):
        if path.find('/') is -1:
            value = float(path)
        else:
            value = float(path[:path.find('/')])
        data[action[i]] = float(value)
        path = path[path.find('/')+1:]

    with open('hallled/data/request.txt', 'w') as f:
        json.dump(data, f)

def translate(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return int(rightMin + (valueScaled * rightSpan))
