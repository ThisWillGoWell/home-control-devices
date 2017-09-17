

import time
from microdotphat import write_string, clear, show
import Adafruit_MCP9808.MCP9808 as MCP9808
import RPi.GPIO as GPIO
import json
import math
import ControlWebsocket
import threading

#Program Constants
DEBUG = True
SERVER_ADDRESS = 'ws://192.168.1.10:8080/ws'
UPDATE_RATE = 1 #server update once a second
READ_RATE = 2	#Read rate for sensor evry 2 seconds


#Update times for gettting system Info
nextReadTime   = time.time()
roomTemp = 0
tempTemp = 68


timeoutLen = 5
timeoutTime = 0
change = True
state = []
toggle = True

#GPIO Map

AC_PIN = 21
FAN_PIN = 20
HEAT_PIN = 16

pins= {}
pins['acState'] = AC_PIN
pins['fanState'] = FAN_PIN
pins['heatState'] = HEAT_PIN
    
startTime = time.time();



class hvacSystem(threading.Thread):

    socket = None
    ac = False
    heat = False
    fan = False
    sensor = MCP9808.MCP9808()


    def __init__(self):
        write_string("start",kerning=False)
        time.sleep(1);
        threading.Thread.__init__(self)
        self.threadID = 'HVAC system'
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(AC_PIN, GPIO.OUT)
        GPIO.setup(FAN_PIN, GPIO.OUT)
        GPIO.setup(HEAT_PIN, GPIO.OUT)
        self.sensor = MCP9808.MCP9808()
        self.sensor.begin()

        self.socket = ControlWebsocket.serverSocket()
        self.socket.daemon = True
        self.socket.start()
        #wait for 1 seconds for the service to configure
        time.sleep(1)
        self.init_values()
        self.roomTemp = self.sensor.readTempC()
        self.updateDisplay()
        
        self.wasConncetd = True

    def init_values(self):
       
        currentState = {}
        if self.socket.is_connected():
            self.socket.get('HVAC','state')
            currentMsg = None
            while currentMsg is None:
                currentMsg = self.socket.get_message()
            currentState = json.loads(currentMsg)['payload']
            self.socket.subscribe('HVAC','acState')
            self.socket.subscribe('HVAC','fanState')
            self.socket.subscribe('HVAC','heatState')
            self.socket.subscribe('HVAC','systemTemp')


        else:
            print("Using offline state")
            currentState = {}
            currentState['acState'] = False
            currentState['heatState'] = False
            currentState['fanState'] = False
            currentState['systemTemp'] = 20
            currentState['roomTemp'] = 20

        print(currentState)
        
        GPIO.output(AC_PIN,currentState['acState'])
        GPIO.output(FAN_PIN,currentState['heatState'])
        GPIO.output(HEAT_PIN,currentState['fanState']) 
        self.systemTemp = currentState['systemTemp']
        self.roomTemp = currentState['roomTemp']
        self.updateDisplay()

    def run(self):
        while True:
            if self.socket.is_connected():
                if not self.wasConncetd:
                    self.init_values()
                    self.wasConncetd = True
                currentMsg = self.socket.get_message()
                if currentMsg is not None:
                    self.processMsg(currentMsg)
            else:
                self.offlineProgram()
                self.wasConncetd = False
                time.sleep(3)

            self.readSensor()
            time.sleep(1)
                
    def processMsg(self, currentMsg):
        msg = json.loads(currentMsg)
        print(msg)
        if 'alert' in msg:
            if msg['request']['what'] == 'acState':
                GPIO.output(AC_PIN, msg['payload'])
            elif  msg['request']['what'] == 'fanState':
                GPIO.output(FAN_PIN, msg['payload'])
            elif  msg['request']['what'] == 'heatState':
                GPIO.output(HEAT_PIN, msg['payload'])
            elif msg['request']['what'] == 'systemTemp':
                self.systemTemp = msg['payload']
                self.updateDisplay()

        

    def readSensor(self):
        if abs(self.roomTemp - self.sensor.readTempC()) > 0.25:
            self.roomTemp = self.sensor.readTempC()
            if self.socket.connected:   
                self.socket.set('HVAC','roomTemp',self.roomTemp)
            self.updateDisplay()

    def updateDisplay(self):
        write_string( str(self.systemTemp)[0:2]+"  " + str(self.roomTemp)[0:2] , kerning=False)
        show()

    def offlineProgram(self):
        if self.roomTemp < self.systemTemp - 5:
            GPIO.output(FAN_PIN, True)
            GPIO.output(HEAT_PIN, True)
        else:
            GPIO.output(FAN_PIN, False)
            GPIO.output(HEAT_PIN, False)

def main():
    system = hvacSystem()
    system.daemon = True
    system.start()
    while(True):
        pass

if __name__ == '__main__':
    main()
	



	
