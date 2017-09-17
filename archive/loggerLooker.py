import sys
import json
import matplotlib.pyplot  as plot
import numpy as np


timestamps = []
temps = []
ac = []
heat = []

for line in open('log.txt'):
	try:
		print(line.strip().split('\t'))
		state = json.loads(line.strip().split('\t')[1])
		timestamp = line.strip().split('\t')[0]		
		timestamps.append(timestamp)
		temps.append(float(state['settings']['roomTemp']))
		ac.append(state['settings']['ac'])
		heat.append(state['settings']['heat'])
	except Exception:
		pass

print(temps)

plot.scatter(range(0, len(temps)),temps)
plot.show()
