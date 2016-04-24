import sys
import serial
import logging
import struct
import binascii
import queue
from time import sleep

log = logging.getLogger(__name__)

#start packet is 8 bytes
#0-2 start sequence
#3 action
#4 number of payload packets
#5 crc
#padded with \x00

#payload packet max 40 bytes
#0-30 payload
#31-39 crc (padded)

#end packet is 3 bytes
#0-2 end sequence

class SerialCommand:
    SERIAL_START = "*_*"
    SERIAL_END = "_*_"
    POLYNOMIAL = 0x1021
    PRESET = 0
    SERIAL_PORT = "/dev/ttyACM1"
    # SERIAL_PORT = "/dev/tty.Bluetooth-Incoming-Port"

    def __init__(self):
        self.ser = serial.Serial(self.SERIAL_PORT, 115200, timeout=5)
        self.actions = {'HSLM': 'h', 'RGBM':'r', 'GET':'g'}
        self._tab = [ self._initial(i) for i in range(256) ]
        self.q_in = queue.Queue()
        # log.debug(self._tab)

    def build_command(self):
        pass

    def sendHSLM(self, hue, saturation, lightning, modulo=1):
        # command = self.action['HSLM'] + hue + saturation + lightning + modulo
        # payload = {'hue':hue, 'saturation':saturation, 'lightning':lightning, 'modulo':modulo}
        payload = bytearray()
        payload.append(hue)
        payload.append(saturation)
        payload.append(lightning)
        payload.append(modulo)
        action = self.actions['HSLM']
        start_packet = self.build_start_packet(action,payload)
        payload_packet=self.build_payload(action, payload)
        end_packet = self.build_end_packet(action, payload)
        # command = self.SERIAL_START + self.padTo16(core) + self.SERIAL_END
        response = self.send(start_packet)
        log.debug("start packet response: %s", response)
        response = self.send(payload_packet)
        log.debug("payload packet response: %s", response)
        # self.send(end_packet)
        return response

    def sendRGBM(self, red, green, blue, modulo=1):
        # command = self.action['HSLM'] + hue + saturation + lightning + modulo
        # payload = {'hue':hue, 'saturation':saturation, 'lightning':lightning, 'modulo':modulo}
        payload = bytearray()
        payload.append(red)
        payload.append(green)
        payload.append(blue)
        payload.append(modulo)
        action = self.actions['RGBM']
        start_packet = self.build_start_packet(action,payload)
        payload_packet=self.build_payload(action, payload)
        end_packet = self.build_end_packet(action, payload)
        # command = self.SERIAL_START + self.padTo16(core) + self.SERIAL_END
        response = self.send(start_packet)
        log.debug("start packet response: %s", response)
        response = self.send(payload_packet)
        log.debug("payload packet response: %s", response)
        # self.send(end_packet)
        return response

    def getStatus(self):
        action = self.actions['GET']
        start_packet = self.build_start_packet(action)
        response = self.send(start_packet)
        return response

    #start packet is 8 bytes
    #0-2 start sequence
    #3 action
    #4 number of payload packets
    #5 crc
    #padded with \x00
    def build_start_packet(self, action=None, payload=None):
        packet = bytearray(self.SERIAL_START, encoding='UTF-8') # 0-2
        packet.append(ord(action)) #3
        if payload:
            payload_len = len(payload)
            # log.debug("payload length: %i", payload_len)
            packet.append(payload_len) #4

        # crc = self.crc(packet)
        # packet += str(crc)
        #xx
        packet = struct.pack('8s',packet)
        # log.debug("start packet is: %s", packet)
        return packet

    def build_payload(self, action, payload):
        packet = bytearray(payload)
        crc = binascii.crc32(packet)
        # log.debug(crc)
        # log.debug(type(crc))
        crc_modded = crc%255;
        log.debug(crc_modded)
        # log.debug(type(crc_modded))
        packet.append(0)
        packet.append(crc_modded)
        packet = struct.pack('40s',packet)
        log.debug("payload packet: %s .", packet)
        return packet

    def build_end_packet(self, action, payload):
        packet = bytearray(self.SERIAL_END, encoding='UTF-8')
        log.debug("end packet: %s .", packet)
        return packet

    def send(self, packet):
        response = ""
        self.ser.write_timeout=5

        log.debug(self.ser)
        if not self.ser.isOpen():
            self.ser.open()

        if packet is not None:
            log.debug("writing %s to serial", packet)
            # log.debug("writing %s to serial (encoded)", packet.encode())
            self.ser.write(packet)
            self.ser.flushOutput()

        #wait 10 milli secs for data to arrive
        sleep(0.010)
        log.debug(self.ser.in_waiting)
        r = ""
        while self.ser.in_waiting > 0:
            try:
                r = self.ser.read(self.ser.in_waiting)
                response += r.decode()
                break
            except UnicodeDecodeError:
                log.debug("error decoding response: %s ", r)


        self.ser.reset_input_buffer();
        # log.debug("got response %s", response)
        #self.ser.close()
        return response





# crc stuff
    def _initial(self, c):
        crc = 0
        c <<= 8
        for j in range(8):
            if (crc ^ c) & 0x8000:
                crc = (crc << 1) ^ self.POLYNOMIAL
            else:
                crc <<= 1
            c <<= 1
        return crc

    def _update_crc(self, crc, c):
        cc = 0xff & c

        tmp = (crc >> 8) ^ cc
        crc = (crc << 8) ^ self._tab[tmp & 0xff]
        crc &= 0xffff
        #print (crc)

        return crc

    def crc(self, message):
        crc = self.PRESET
        for c in message:
            crc = self._update_crc(crc, ord(c))
        return crc

    def crcb(self, *i):
        crc = self.PRESET
        for c in i:
            crc = self._update_crc(crc, c)
        return crc



