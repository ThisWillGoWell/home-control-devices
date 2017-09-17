#this is the pi Simulator
#will handel cross talk communication between the Springboot and python
#simulating the Temp and LCD input

#Mabe? Run only on linux

#Pyhton =>	Current Temp 	=> Java
#		<=  SetTemp			=>
#		<=  Mode			=> 
#


import urllib.request as request
import json
import random

SERVER_ADDRESS = 'http://localhost:8080'

SERVER_ENDPOINTS = ['/getState','/setSystemTemp','/setRoomTemp', '/setAc', '/setHeat', '/setFan', '/setPower']


staet = []
'''
get the current state of the system
'''
def getState():
	url = SERVER_ADDRESS + SERVER_ENDPOINTS[0]
	response = request.urlopen(url)
	jsonStr = str(response.read())[2:-1]
	print(jsonStr)

	state = json.loads(jsonStr)
	systemTemp = state["settings"]["systemTemp"]


def setSystemTemp(temp):
	url = SERVER_ADDRESS + SERVER_ENDPOINTS[1]
	response = request.urlopen(url + '?temp=' + str(temp))
	

def setRoomTemp(tmep):
	url = SERVER_ADDRESS + SERVER_ENDPOINTS[2]
	response = request.urlopen(url + '?temp=' + str(temp))

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



getState()
setSystemTemp(random.randrange(30,60,1))
getState()

