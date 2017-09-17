

import RPi.GPIO as GPIO
import time
import Adafruit_MCP4725
dac = Adafruit_MCP4725.MCP4725()

from smbus2 import SMBus


POWER_READ = 20
LOW_WATER_READ = 21
BREW_10_READ = 26
LID_TOGGLE = 19

VCC = 4.8
voltages = {'power': 2.5, 'brew10' : 0.500}



GPIO.setmode(GPIO.BCM)
GPIO.setup(POWER_READ, GPIO.IN)
GPIO.setup(LOW_WATER_READ, GPIO.IN)
GPIO.setup(BREW_10_READ, GPIO.IN)
GPIO.setup(LID_TOGGLE, GPIO.OUT)

GPIO.output(LID_TOGGLE, True)
bus = SMBus(1)

def voltage(s):
	return int((voltages[s]+ 0.3)/VCC * 0x0FFF)

def toggle_lid():
	GPIO.output(LID_TOGGLE, False)
	time.sleep(1)
	GPIO.output(LID_TOGGLE, True)

def toggle_power():
	dac.set_voltage(voltage('power'))
	time.sleep(1)
	dac.set_voltage(0)

def toggle_brew10():
	dac.set_voltage(voltage('brew10'))
	time.sleep(1)
	dac.set_voltage(0)

def power():
	return not GPIO.input(POWER_READ)

def brewLED():
	return not GPIO.input(BREW_10_READ)

def brewCoffee():
	
	while not power():
		toggle_power()
		print(power())
		time.sleep(1)

	while not brewLED():
		time.sleep(2)

	canBrew = False
	while not canBrew:
		currentLED = brewLED()
		print(currentLED)
		time.sleep(.5)
		if currentLED != brewLED():
			canBrew = True
		else:
			toggle_lid()
			time.sleep(5)
		time.sleep(.1)
	toggle_brew10()

	while brewLED():
		time.sleep(0.1)

	toggle_power()

	

brewCoffee()

