import logging
import serial
from pyramid.response import Response
logger = logging.getLogger("pyramid.app.hall_led")
logger.setLevel(logging.DEBUG)

def hello_world(request):
    return Response('Hello %(name)s!' % request.matchdict)

def api_led(request):
	resp = led(request.matchdict['command'], request.matchdict['operator'], request.matchdict['amount'])
	logger.debug(resp)
	return Response(resp)
	
def led(command, operator, amount):
	#with serial.Serial("/dev/ttyACM0", 9600, timeout=2) as ser:
	ser = serial.serial_for_url("/dev/ttyACM1", do_not_open=True)
	try:
		ser.open()
	except serial.SerialException as e:
		sys.stderr.write("Could not open serial port {}: {}\n".format(ser.name, e))
		sys.exit(1)
	#ser.isOpen()
	ser.write(command.encode())
	ser.write(operator.encode())
	ser.write(chr(int(amount)).encode())
	ser.write("~".encode());
	serResponse = ""
	serResponse = ser.read(100)
	ser.flushInput()
	ser.close()
	return serResponse
