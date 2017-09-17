

import time
"""
from microdotphat import write_string, clear, show
import Adafruit_MCP9808.MCP9808 as MCP9808
import RPi.GPIO as GPIO
"""	
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

AC_PIN = 20
FAN_PIN = 4
HEAT_PIN = 21

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
    sensor = None #MCP9808.MCP9808()
    
    def __init__(self):
        threading.Thread.__init__(self)
        self.threadID = 'HVAC system'
        self.socket = ControlWebsocket.serverSocket()
        self.socket.start()
        while not self.socket.is_connected():
            pass
        
        """
	GPIO.setmode(GPIO.BCM)
	
	GPIO.setup(AC_PIN, GPIO.OUT)
	GPIO.setup(FAN_PIN, GPIO.OUT)
	GPIO.setup(HEAT_PIN, GPIO.OUT)

	GPIO.output(AC_PIN,False)
	GPIO.output(FAN_PIN,False)
	GPIO.output(HEAT_PIN,False)
	"""
	
        self.socket.get('HVAC','state')
        currentMsg = None
        while currentMsg is not None:
            currentMsg = self.socket.get_message()
            if DEBUG:
                print(currentState)
        
        #GPIO.output(AC_PIN,currentState['payload']['acState'])
        #GPIO.output(FAN_PIN,currentState['payload']['acState'])
        #GPIO.output(HEAT_PIN,currentState['payload']['acState'])             
        self.socket.subscribe('HVAC','acState')
        self.socket.subscribe('HVAC','heatState')
        self.socket.subscribe('HVAC','fanState')
        #self.sensor.begin()
        
    def run(self):
        while True:
            if self.socket.is_connected():
                currentMsg = self.socket.get_message()
                if currentMsg is not None:
                    self.processMsg(currentMsg)
                
    def processMsg(self, currentMsg):
        msg = json.loads(currentMsg)
        print(msg)
        

    def readSensor():
            global startTime
            global nextReadTime
            if time.time() > nextReadTime:
                    if ON_PI:
                            setRoomTemp(sensor.readTempC())
                    else:
                            setRoomTemp( time.time() - startTime /60)
                    nextReadTime += 1


    def display():
            global roomTemp
            global systemTemp
            if ON_PI:
                    write_string( str(systemTemp)[0:2]+"  " + str(roomTemp)[0:2] , kerning=False)
                    show()


def main():
    system = hvacSystem()
    system.start()


if __name__ == '__main__':
    main()
	



	
