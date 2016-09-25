"""
Defines the routes available.
Methods which are annotated with "renderer='json'" are api methods
"""
import logging
import json
import os.path

from pyramid.view import view_config

from hallled.async.GatewayClient import GatewayClient

log = logging.getLogger(__name__)


@view_config(route_name='home', renderer='templates/hallled.pt')
def home_view(request):
    """
    The home view.

    :param request:
    :return: dict with variables to be rendered
    """
    return {'project': 'HallLed'}

@view_config(route_name='react', renderer='templates/react.pt')
def react_view(request):
    """
    The home view.

    :param request:
    :return: dict with variables to be rendered
    """
    return {'project': 'HallLed'}


@view_config(route_name='api_led_hslm', renderer='json', request_method="POST")
def api_post_led_hsla(request):
    """

    :param request:
        request.matchdict['hue'] the hue value to set
        request.matchdict['saturation'] the saturation to set
        request.matchdict['lightning'] the lightning to get
        request.matchdict['modulo'] the modulo
    :return:
    """

    log.debug(request.body)

    data = request.body.decode("utf-8")
    save_data(data, "hslm")
    body = json.loads(data)
    color = body["color"]
    mod = body["mod"]
    hsl = color["hsl"]
    hue = translate(float(hsl["hue"]), 0, 360, 0, 254)
    saturation = translate(float(hsl["saturation"]), 0, 1, 0, 254)
    lightning = translate(float(hsl["lightning"]), 0, 1, 0, 254)
    modulo = int(mod)
    if modulo == 0:
        modulo = 1
    # log.debug("hue: %i, saturation: %i, lightning: %i, modulo: %i", hue, saturation, lightning, modulo)

    # writeToPipe([104, hue, saturation, lightning, modulo])
    write_to_socket([104, hue, saturation, lightning, modulo])
    response = ""
    return dict(arduino="ok")

@view_config(route_name='api_led_hslm', renderer='string', request_method="GET")
def api_get_led_hsla(request):
    return load_data("hslm")

@view_config(route_name='api_led_rgbm', renderer='json')
def api_led_rgb(request):
    # rememberRequest(request)
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

    return dict(arduino="")

@view_config(route_name='api_named_pipe', renderer='json', request_method='POST')
def api_named_pipe(request):
    """

    :param request:
        request.matchdict['data'] the data to be written to the named pipe
    :return: json data describing the result
    """
    fifo_write = open('/tmp/to_bridge', 'ab', 0)
    data = request.body

    log.debug("pipe data: %s", data)
    bytes_to_write = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
    for item in data.split():
        bytes_to_write.append(int(item))
    log.debug("bytes: %s", bytes_to_write)
    # bytes_to_write = bytearray(parts)
    bytes_written = fifo_write.write(bytes(bytes_to_write))
    log.debug("number bytes written: %i", bytes_written)
    fifo_write.close()

    return dict(pipe='ok')

@view_config(route_name='api_info', renderer='json')
def api_info(request):
    """
    Load the last saved request

    :param request:
    :return: the json payload
    """
    data = ""
    with open('hallled/data/request.txt', 'r') as f:
        data = json.load(f)

    # define default rgbm values
    if not data:
        data = {'r':30, 'g':30, 'b':20, 'm':10}

    return data


@view_config(route_name="api_options", renderer="json", request_method="POST")
def api_post_options(request):
    save_data(request.body.decode("utf-8"), 'options')
    options = json.loads(request.body.decode("utf-8"))
    sensors = options["sensors"]
    if sensors["motionSensor"] is not None:
        motionSensor = sensors["motionSensor"]
        log.debug(motionSensor["enabled"])
        log.debug(motionSensor["timeout"])

        command = []
        command.append(111) # append an "o" for option command
        command.append(115) # append a "s" to indicate sensor option
        command.append(0) # zero is the motion sensor (for the time being)
        n = len(motionSensor)
        command.append(n) # append the number of commands

        for key, value in motionSensor.items(): # append all values from the request
            c = ord(key[:1] )# first character of the property
            v = value # value of the propery
            command.append(c)
            command.append(v)

        log.debug(command)
        #writeToPipe(command)  # "o" -> option (char),
                              # "s" -> sensor (char),
                              # i -> sensor number (int),
                              # n -> number of commands (int)
                              # c -> command ( "e" -> enabled, "t" -> timeout ) (char)
                              # v -> value (int)
        write_to_socket(command)
    log.debug(options)
    return dict(arduino="ok")


@view_config(route_name="api_options", renderer='string', request_method="GET")
def api_get_options(request):
    return load_data("options")

@view_config(route_name="socket_test", renderer="json", request_method="GET")
def socket_test(request):
    server = GatewayClient()
    server.write("socket test message")
    return server.info()


# deprecated
def writeToPipe(data):
    fifo_write = open('/tmp/to_bridge', 'ab', 0)
    bytes_to_write = [0, 0, 0, 0, 0, 1, 1, 1, 1, 1]
    for item in data:
        bytes_to_write.append(int(item))
    log.debug("write to pipe: %s", bytes_to_write)
    bytes_written = fifo_write.write(bytes(bytes_to_write))
    log.debug("number bytes written: %i", bytes_written)
    fifo_write.close()
    return bytes_written


def write_to_socket(data):
    log.debug("write_to_socket")
    gateway_client = GatewayClient()
    log.debug("got gateway client")
    gateway_client.write(data)
    return len(data)



def rememberHSLRequest(request):
    """
    Saves the request payload as a json data.

    :param request:
    :return: none
    """
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


def save_data(data, filename):
    with open('hallled/data/' + filename + '.txt', 'w') as f:
        f.write(data)


def load_data(filename):
    file = 'hallled/data/' + filename + '.txt'

    if(os.path.isfile(file)):
        with open(file, 'r') as f:
            return f.read()

    return None


def translate(value, leftMin, leftMax, rightMin, rightMax):
    """
    Translates values from a given range to a defined range.

    :param value: value to translate
    :param leftMin: given min
    :param leftMax:  given max
    :param rightMin:  defined min
    :param rightMax:  defined max
    :return: translated value
    """
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return int(rightMin + (valueScaled * rightSpan))
