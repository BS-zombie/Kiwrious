import serial
import serial.tools.list_ports

import time, struct

TYPES = ['UV', 'BODY TEMP', 'COLOUR', 'CONDUCTIVITY', 'HEART RATE', 'VOC', 'HUMIDITY', 'SOUND']

class Found(Exception):
    pass

class Sensor:
    def __init__(self):
        print("Scanning for sensor")
        ports = serial.tools.list_ports.comports()
        self.sensor = None
        try:
            for port in ports:
                name = port.device
                try:
                    print(name)
                    ser = serial.Serial(port = name, baudrate=115200,bytesize=8, timeout=2, stopbits=serial.STOPBITS_ONE)
                except:
                    continue
                for n in range(50):
                    HEADER = int.from_bytes(ser.read(2),'little')
                    print(HEADER)
                    if HEADER == 2570:
                        self.sensor = ser
                        print("Found Sensor!")
                        raise Found
        except Found:
            self.connected = True
        else:
            self.connected = False
            print("Couldn't find sensor")

    def close(self):
        """Closes serial port"""
        if not self.connected:
            print("Isn't connected to sensor!")
        self.sensor.close()
        self.connected = False

    def get_packet(self, timeout = 5):
        """Gets a packet from sensor and returns it in a dictionary"""
        if not self.connected:
            print("Sensor not connected")
            return None
        HEADER = 0
        start_time = time.time()
        while HEADER != 2570:
#            print('Scanning for packet')
            if (time.time() - start_time) > 5:
                raise TimeoutError
            try:
                HEADER = int.from_bytes(self.sensor.read(2),'little')
            except serial.serialutil.SerialException:
                print("Sensor disconnected")
                self.close()
                return
        TYPE = [int.from_bytes(self.sensor.read(1),'little') for i in range(2)][::-1]
        LEN = int.from_bytes(self.sensor.read(2),'little')
        DATA_BYTES = [self.sensor.read(2) for i in range(8)]
        DATA = [int.from_bytes(datum ,'little') for datum in DATA_BYTES]
        FLOAT_1 = DATA_BYTES[0] + DATA_BYTES[1]
        FLOAT_2 = DATA_BYTES[2] + DATA_BYTES[3]
        SEQ = int.from_bytes(self.sensor.read(2),'little')
        FOOTER = int.from_bytes(self.sensor.read(2),'little')
        if TYPE[0] != 1:
            return
        TYPE = TYPES[TYPE[1] - 1]
        
        if TYPE == 'UV':
            return {'Lux' : struct.unpack('<f', FLOAT_1)[0] , 'UV' : struct.unpack('<f', FLOAT_2)[0]}
        elif TYPE == 'BODY TEMP':
            return {'Temperature' : DATA[0]/100}
        elif TYPE == 'COLOUR':
            return dict(zip(('Red', 'Green', 'Blue', 'White'),DATA[:4]))
        elif TYPE == 'CONDUCTIVITY':
            return {'Conductivity' : DATA[0] * DATA[1]}
        elif TYPE == 'HEART RATE':
            return {'BPM' : DATA[0]/100}
        elif TYPE == 'VOC':
            return {'VOC' : DATA[0], 'CO2' : DATA[1]}
        elif TYPE == 'HUMIDITY':
            return {'Temperature' : DATA[0] / 100, 'Humididty' : DATA[1] / 100}
        elif TYPE =='SOUND':
            return {'Volume' : DATA[0]/ 100}

if __name__ == "__main__":
    sensor = Sensor()
    while True:
        print(sensor.get_packet())
    sensor.close()