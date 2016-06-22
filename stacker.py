import re
import os
import time
import signal
import sys
import drive
import flow
import shaker

'''
Should do:
- Drive to start position without feeding
- Start feeder
- Build stockpile by file and measurement of amount
- log amount per color and position
- allow user to pause (e.g. because something needs fixing but user want to continue later)
'''

currentPos = 0
stop = False
startIntensity = 0.15
minIntensity = 0.11
maxIntensity = 0.30
frequency = 42.6

def getProgram(file):
	file = open(file, 'r')
	program = []
	for line in file:
		values = line.split()
		program.append((float(values[0]), float(values[1])))
	return program

def stack(file):
	global currentPos
	global stop
	
	drive.blockingMoveToStockpile(0)

	program = getProgram(file)
	programStep = 1
	
	flow.init()
	shaker.init()

	intensity = startIntensity
	shaker.shake(frequency, intensity)

	currentStepMaterial = 0
	lastCheck = flow.now()
	
	logFile = open(file + " " + str(time.time()) + " stack.csv", "w")
	
	while (not stop and programStep < len(program)):
		lastPos = program[programStep - 1][0]
		nextPos = program[programStep][0]
		targetStepMaterial = program[programStep][1]
		line = flow.read()
		currentFlow = flow.getLastSum()

		currentPos = lastPos + (nextPos - lastPos) * (currentStepMaterial / targetStepMaterial)
		line += "\t" + str(currentPos) # because of pollWithoutCapture, else: str(drive.getPosInStockpile())
		logFile.write(line + "\n")
		drive.pollWithoutCapture()
		drive.moveToStockpile(currentPos)
		print('Step ' + str(programStep) + '/' + str(len(program) - 1))
		print(str(currentStepMaterial) + ' of ' + str(targetStepMaterial) + ' mm3, ' + str(round(100 * currentStepMaterial / targetStepMaterial)) + '% @ ' + str(round(currentFlow)) + ' mm3/s')
		print('Position: ' + str(round(100 * currentPos)) + '%')
		
		now = flow.now()
		currentStepMaterial += round(currentFlow * (now - lastCheck))
		lastCheck = now

		d = 1. - 2. * flow.getFeedback()
		intensity = max(minIntensity, min(maxIntensity, intensity + d * 0.001))
		shaker.shake(frequency, intensity)
		print('Feedback: ' + str(int(100.0 * flow.getFeedback())) + '%, Intensity: ' + str(int(100 * intensity)) + '%')
		
		if (currentStepMaterial > targetStepMaterial):
			currentStepMaterial -= targetStepMaterial # add overflow material to next step
			programStep += 1
	
	print('cleaning up')
	shaker.cleanup()
	flow.cleanup()
	logFile.close()
	time.sleep(2)
	drive.blockingMoveToStockpile(0)
	print('done')
