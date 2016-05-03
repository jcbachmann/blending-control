import time
import signal
import flow
import drive
import shaker

'''
Should do:
- Ask user to set down feeder to reclaim position
- Feed until about 1400000 with constant speed
- Log time, position, particles
- Drive back to position 0
- allow user to pause
'''

stop = False

def reclaim(file):
	global currentPos
	global stop

	drive.blockingMoveToStockpile(1)
	shaker.init()
	shaker.shake(42.6, 0.25)
	flow.init()
	
	drive.poll()
	drive.run(30)
		
	currentMaterial = 0
	minPrintTimeDiff = 1
	lastPrint = time.time() - minPrintTimeDiff
	lastCheck = time.time()
	
	logFile = open(file + " " + str(time.time()) + " reclaim.csv", "w")
	
	while (not stop and drive.getPosInStockpile() < 2.2):
		drive.poll()
		line = flow.read()
		now = time.time()
		currentFlow = flow.getLastSum()
		line += "\t" + str(drive.getPosInStockpile())
		logFile.write(line + "\n")
		
		if (now > lastPrint + minPrintTimeDiff):
			lastPrint = now
			print(str(currentMaterial) + ' mm3 @ ' + str(currentFlow) + ' mm3/s')
		
		currentMaterial += round(currentFlow * (now - lastCheck))
		lastCheck = now
	
	logFile.close()
	shaker.cleanup()
	flow.cleanup()
	drive.blockingMoveToStockpile(0)
	print('done')
