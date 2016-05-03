import subprocess
import os
import time
from datetime import datetime
import statistics

colorcount = None
flow = 0
timestamp = 0
latestFlows = []
latestFlowCount = 24
#latestFlowInit = 0.05
#flowFactor = 37000.0
flowFactor = 110000.0

def init():
	global colorcount
	colorcount = subprocess.Popen(["colorcount"], stdout=subprocess.PIPE, stdin=subprocess.PIPE)
#	for i in range(0,latestFlowCount):
#		latestFlows.append(latestFlowInit)

def read():
	global colorcount
	global flow
	global timestamp
	global latestFlows
	line = colorcount.stdout.readline().decode("UTF-8") # Blocking call
	print(line)
	framenumber, framemicroseconds, gray, red, blue, yellow, undefined = tuple(line.split())
	flow = (float(red) + float(blue) + float(yellow)) * flowFactor
	latestFlows.append(float(red) + float(blue) + float(yellow))
	if len(latestFlows) > latestFlowCount:
		latestFlows.pop(0)
	timestamp = int(framemicroseconds)
	return framemicroseconds + "\t" + gray + "\t" + red + "\t" + blue + "\t" + yellow + "\t" + undefined

def now():
	global timestamp
	return timestamp / 1000000

def getFeedback():
	global latestFlows
	f = statistics.median(latestFlows) / 0.035
	if f > 1:
		f = 1
	return f

def getLastSum():
	global flow
	return flow

def cleanup():
	colorcount.terminate()
	colorcount.wait()
