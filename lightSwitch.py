
import RPi.GPIO as GPIO
import requests as request
import time
#state = {'off' : 0, 'low' : 1, 'bright' : 2, 'auto' : 3}

##modes = {'off' : 0, 'low' : 1, 'bright' : 2, 'standard' : 3, 'rainbow' : 4, 'party' : 5}

modes = ['off', 'dim', 'bright', 'standard', 'rainbow', 'party']
states = ['off', 'dim', 'bright', 'auto']

SWITCH_1 = 36
SWITCH_2 = 35
TRIGGER_DELAY = 200
CYCLE_OFFSET = 3

SERVER_ADDRESS = 'http://192.168.1.18:8080'

def t():
	return time.time() * 1000

class Switch(object):
	currentMode = 0;
	switch1UpdateTime = 0;
	switch2UpdateTime = 0;

	switch1Trigger = False
	switch2Trigger = False

	switch1Value = False
	switch2Value = False

	def __init__(self):
		#init pins
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(SWITCH_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
		GPIO.setup(SWITCH_2, GPIO.IN,pull_up_down=GPIO.PUD_UP)

		self.switch2UpdateTime = t();
		self.switch1UpdateTime = t();

		self.switch1Value =  GPIO.input(SWITCH_1)
		self.switch2Value =  GPIO.input(SWITCH_2)
		self.selectIndex = 3
		self.currentMode = None
		self.currentState = None
		self.stateMachine()
		self.setMode()

	def stateMachine(self):
		if self.currentState == None:
			if self.switch1Value and self.switch2Value:
				self.currentMode = modes[2]
				self.currentState = states[2]

			elif self.switch1Value:
				#only top switch
				self.currentMode = modes[3]
				self.currentState = states[3]
				self.selectIndex = 3

			elif self.switch2Value:
				#only bottom switch
				self.currentMode = modes[1]
				self.currentState = states[1]

			else:
				#off
				self.currentMode = modes[0]
				self.currentState = states[0]				



		elif self.currentState == states[0]:
			#we were in off Mode
			self.selectIndex =0;
			if self.switch1Trigger and self.switch2Trigger :
				if self.switch1Value and self.switch2Value:
					#SHOULD be the only thing here, but check anyways
					self.currentState = states[2]
					self.currentMode = modes[2]
				else:
					print("ERROR, double Trigger in off, not both on")

			elif self.switch1Trigger:
				if self.switch1Value:
					#SHOULD be the only thing here, but check anyways
					self.currentState = states[3]
					self.currentMode = modes[3]
				else:
					print("ERROR, 1 Trigger in off, not on")

			elif self.switch2Trigger:
				if self.switch2Value:
					#SHOULD be the only thing here, but check anyways
					self.currentState = states[1]
					self.currentMode = modes[1]
				else:
					print("ERROR, 2 Trigger in off, not on")

		elif self.currentState == states[1]:
			#Were in Dim
			if self.switch1Trigger and self.switch2Trigger :
				if self.switch1Value and not self.switch2Value:
					#SHOULD be the only thing here, but check anyways
					self.currentState = states[3]
					self.currentMode = modes[3]
				else:
					print("ERROR, double Trigger in Dim, 1 True, 2 False")

			elif self.switch1Trigger:
				if self.switch1Value:
					#SHOULD be the only thing here, but check anyways
					self.currentState = states[2]
					self.currentMode = modes[2]
				else:
					print("ERROR, 1 Trigger in Dim, not on")

			elif self.switch2Trigger:
				if not self.switch2Value:
					#SHOULD be the only thing here, but check anyways
					self.currentState = states[0]
					self.currentMode = modes[0]
				else:
					print("ERROR, 2 Trigger in Dim, not off")

		elif self.currentState == states[2]:
			#Were in Bright
			if self.switch1Trigger and self.switch2Trigger :
				if not self.switch1Value and not self.switch2Value:
					#SHOULD be the only thing here, but check anyways
					self.currentState = states[0]
					self.currentMode = modes[0]
				else:
					print("ERROR, double Trigger in Bright, both not off")

			elif self.switch1Trigger:
				if not self.switch1Value:
					#SHOULD be the only thing here, but check anyways
					self.currentState = states[1]
					self.currentMode = modes[1]
				else:
					print("ERROR, 1 Trigger in Bright, not off")

			elif self.switch2Trigger:
				if not self.switch2Value:
					#SHOULD be the only thing here, but check anyways
					self.currentState = states[3]
					self.currentMode = modes[3]
				else:
					print("ERROR, 2 Trigger in Bright, not off")

		elif self.currentState == states[3]:
			#Were in wtf mode
			if self.switch1Trigger:
				if not self.switch1Value:
					if self.switch2Value:
						self.currentMode = modes[1]
						self.currentState = states[1]
					else:
						self.currentState = states[0]
						self.currentMode = modes[0]
				else:
					print("ERROR, double Trigger in WTF mode, 1 not off")

			elif self.switch2Trigger:
				self.selectIndex = CYCLE_OFFSET +  (self.selectIndex + 1 )%(len(modes) - CYCLE_OFFSET) 
				self.currentMode = modes[self.selectIndex]

		self.switch2Trigger = False
		self.switch1Trigger = False

	def setMode(self):
		print(self.currentMode, self.currentState)
		url = SERVER_ADDRESS + '/set?system=lights&what=mode&to=' + self.currentMode
		response = request.get(url)





	def run(self):
		while True:
			if GPIO.input(SWITCH_1) != self.switch1Value:
				self.switch1Trigger = True
				self.switch1Value =  GPIO.input(SWITCH_1)
				self.switch1UpdateTime = t()

			if GPIO.input(SWITCH_2) != self.switch2Value:
				self.switch2Trigger = True
				self.switch2Value =  GPIO.input(SWITCH_2)
				self.switch2UpdateTime = t()

			if (self.switch1Trigger or self.switch2Trigger) and (t() - max(self.switch1UpdateTime, self.switch2UpdateTime) > TRIGGER_DELAY):
				self.stateMachine()
				self.setMode()




def main():
	s = Switch()
	s.run()

main()