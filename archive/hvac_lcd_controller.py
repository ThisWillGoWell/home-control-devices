
#TODO 9/20/2016
#need to get this and the jar running on the pi.... 

import time
import Adafruit_CharLCD as LCD
import Adafruit_MCP9808.MCP9808 as MCP9808
import urllib as request
import json
import RPi.GPIO as GPIO
import math


#Program Constants
SERVER_ADDRESS = 'http://localhost:8080'
SERVER_ENDPOINTS = SERVER_ENDPOINTS = ['/getState','/setSystemTemp','/setRoomTemp', '/setAc', '/setHeat', '/setFan', '/setPower']
lcd = LCD.Adafruit_CharLCDPlate()
sensor = MCP9808.MCP9808()

UPDATE_RATE = 1 #server update once a second
READ_RATE = 2	#Read rate for sensor evry 2 seconds


#Update times for gettting system Info
nextUpdateTime = time.time()
nextReadTime   = time.time()
roomTemp = 0

systemTemp = 68
tempTemp = 68

pressedButton = 0
buttonList = [LCD.SELECT, LCD.UP, LCD.DOWN]
buttonStatus = [False, False, False, False]
timeoutLen = 5
timeoutTime = 0
change = True
state = []
toggle = True

#GPIO Map
AC_PIN = 4
FAN_PIN = 21
HEAT_PIN = 20
#Should these be on
ac = False
heat = False
fan = False

#What mode are we in?
acPower = False
heatPower = False
fanPower = False
power = False

#GPIO_DIRECTION

GPIO.setup(AC_PIN, GPIO.OUT)
GPIO.setup(FAN_PIN, GPIO.OUT)
GPIO.setup(HEAT_PIN, GPIO.OUT)

GPIO.output(AC_PIN,False)
GPIO.output(FAN_PIN,False)
GPIO.output(HEAT_PIN,False)



def buttons():
	global toggle
	global tempTemp	
	global timeoutTime	
	global	change	
	global lcd
	global	pressedButton	
	global	buttonList	
	if not toggle:
		if(not lcd.is_pressed(buttonList[pressedButton])):
			change = True
			toggle = True
	else:
		if(lcd.is_pressed(LCD.UP)):
			tempTemp = tempTemp + 1
			pressedButton = 1
			toggle = False
		 	lcd.clear()
			lcd.message( str(tempTemp) + '\x01')
			timeoutTime = time.time() + timeoutLen

		if(lcd.is_pressed(LCD.DOWN)):
			tempTemp = tempTemp -1
			pressedButton = 2
			toggle = False
			lcd.clear()
			lcd.message(str(tempTemp) + '\x01')
			timeoutTime = time.time() + timeoutLen

		if(lcd.is_pressed(LCD.SELECT)):
			setSystemTemp(tempTemp)
			pressedButton = 0
			toggle = False
			lcd.clear()
			lcd.message("Setting temp to: ")
			timeoutTime = time.time() + timeoutLen

def getState():
	global	state	
	url = SERVER_ADDRESS + SERVER_ENDPOINTS[0]
	response = request.urlopen(url)
	jsonStr = str(response.read())
	print(jsonStr)
	state = json.loads(jsonStr)
	systemTemp = state["settings"]["systemTemp"]
	pass

def setSystemTemp(temp):
	url = SERVER_ADDRESS + SERVER_ENDPOINTS[1]
	response = request.urlopen(url + '?temp=' + str(temp))
	pass

def setRoomTemp(temp):
	url = SERVER_ADDRESS + SERVER_ENDPOINTS[2]
	response = request.urlopen(url + '?temp=' + str(temp))
	pass

def setPower(state):
	url = SERVER_ADDRESS + SERVER_ENDPOINTS[6]
	response = request.urlopen(url+'?state=' + str(state))
	pass

def setFan(state):
	url = SERVER_ADDRESS + SERVER_ENDPOINTS[5]
	response = request.urlopen(url+'?state=' + str(state))
	pass

def setHeat(state):
	url = SERVER_ADDRESS  +SERVER_ENDPOINTS[4]
	response = request.urlopen(url + '?state=' + str(state))
	pass

def setAc(state):
	url =  SERVER_ADDRESS + SERVER_ENDPOINTS[3]
	response = request.urlopen(url + '?state=' + str(state))
	pass


def update():
	global	roomTemp
	global	systemTemp	
	global	change	
	global state
	if time.time() > nextUpdateTime:
		url = SERVER_ADDRESS + SERVER_ENDPOINTS[0]
		response = request.urlopen(url)
		jsonStr = str(response.read())
		state = json.loads(jsonStr)

		if systemTemp != state["settings"]["systemTemp"]:
			systemTemp = state["settings"]["systemTemp"]
			change = True

		if float(roomTemp)	 != round(float(state["settings"]["roomTemp"])):
			roomTemp = str(round(float(state["settings"]["roomTemp"])))
			change = True

def readSensor():
	if time.time() > nextReadTime:
		setRoomTemp(sensor.readTempC())

def timeout():
	global	timeoutTime	
	global	change	
	global tempTemp
	global heatPower
	global heat
	global fanPower
	global fan
	global acPower
	global ac

	if time.time() > timeoutTime and change:
		change = False
		tempTemp = float(systemTemp)
		lcd.clear()
		if power == False:
			lcd.message('System off     '+ THEMO_SYMBOL + roomTemp + DEGREE_SYMBOL)
		else:
			if acPower == True:
				lcd.message('Cooling     '+ THEMO_SYMBOL + roomTemp + DEGREE_SYMBOL)
				lcd.message('\n            '+PLAY_PAUSE_SYMBOL + systemTemp + DEGREE_SYMBOL)
			elif heatPower == True:
				lcd.message('Heating     '+ THEMO_SYMBOL + roomTemp + DEGREE_SYMBOL)
				lcd.message('\n            '+PLAY_PAUSE_SYMBOL + systemTemp + DEGREE_SYMBOL)
			elif fanPower == True:
				lcd.message('Fanning     ' + THEMO_SYMBOL + roomTemp + DEGREE_SYMBOL)
				lcd.message('\n            '+PLAY_PAUSE_SYMBOL + systemTemp + DEGREE_SYMBOL)
			else:
				lcd.message('Standby     ' + THEMO_SYMBOL + roomTemp + DEGREE_SYMBOL)
				lcd.message('\n            '+PLAY_PAUSE_SYMBOL + systemTemp + DEGREE_SYMBOL)


def toggleGPIO():
	global state
	global ac
	global fan
	global heat
	global AC_PIN
	global FAN_PIN
	global HEAT_PIN
	global change

	if (state['settings']['ac'] == 'true') != ac:
		ac = not ac
		GPIO.output(AC_PIN,ac)
		change = True
		
	if (state['settings']['fan'] == 'true') != fan:
		fan = not fan
		GPIO.output(FAN_PIN, fan)
		change = True

	if (state['settings']['heat'] == 'true') != heat:
		heat = not heat
		GPIO.output(HEAT_PIN, heat)
		change = True

def mode():
	global state
	global power
	global fanPower
	global heatPower
	global acPower
	global change
	if (state['settings']['power'] == 'true') != power:
		change = True 
		power = not power;

	if (state['settings']['acPower'] == 'true') != acPower:
		change = True
		acPower = not acPower

	if (state['settings']['heatPower'] == 'true') != heatPower:
		change = True
		heatPower = not heatPower

	if (state['settings']['fanPower'] == 'true') != fanPower:
		change = True
		fanPower = not fanPower




#Pre Program Functions
DEGREE_SYMBOL = '\x01'
lcd.create_char(1, [0,8,20,8,0,0,0,0]) #DEGREE
PLAY_PAUSE_SYMBOL = '\x02'
lcd.create_char(2, [0,20,22,23,22,20,0,0]) #PLAY_PAUSE
THEMO_SYMBOL = '\x03'
lcd.create_char(3,[0,4,4,4,4,10,4,0]) #THEMO


lcd.set_color(1.0, 1.0, 1.0)
lcd.clear()
lcd.message('Waiting for connection')
#init sensor
sensor.begin()

update()
tempTemp = float(systemTemp)


while True:
	readSensor()
	buttons()
	update()
	toggleGPIO()
	mode()
	timeout()
	#Update form sever

	



	
