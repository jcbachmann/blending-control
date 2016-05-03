import re
import os
import time
import signal
import sys
import drive
import flow

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

def getProgram(file):
	file = open(file, 'r')
	program = []
	for line in file:
		matches = re.search('(.*)\t(.*)', line)
		program.append((float(matches.group(1)), float(matches.group(2))))
	return program

def stack(file):
	global currentPos
	global stop
	
	drive.init()	
	drive.moveTo(0)
	time.sleep(45)

	program = getProgram(file)
	programStep = 1
	
	flow.init()
	
	currentStepMaterial = 0
	lastCheck = time.time()
	minMoveToTimeDiff = 0
	lastMoveTo = time.time() - minMoveToTimeDiff
	
	while (not stop and programStep < len(program)):
		now = time.time()
		lastPos = program[programStep - 1][0]
		nextPos = program[programStep][0]
		targetStepMaterial = program[programStep][1]
		currentFlow = flow.get(currentPos)
		
		if (now > lastMoveTo + minMoveToTimeDiff):
			currentPos = lastPos + (nextPos - lastPos) * (currentStepMaterial / targetStepMaterial)
			drive.moveTo(currentPos)
			lastMoveTo = now
			print(str(currentStepMaterial) + ' of ' + str(targetStepMaterial) + ' mm3 @ ' + str(currentFlow) + ' mm3/s in step ' + str(programStep) + ', pos: ' + str(round(100 * currentPos)) + '%')
		
		currentStepMaterial += round(currentFlow * (now - lastCheck))
		lastCheck = now
		
		if (currentStepMaterial > targetStepMaterial):
			currentStepMaterial -= targetStepMaterial # add overflow material to next step
			programStep += 1
			print('step: ' + str(programStep))
	
	flow.cleanup()
	drive.moveTo(0)
	print('done')
