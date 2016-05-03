import time
import drive
import shaker
import signal
import flow

'''
Should do:
- Drive to pos -200000
- empty feeder (either recognize or just shake until user stop)
- Ask user to wait for particles at reclaimer funnel
- Drive to position 550000
'''

def dump1():
	drive.blockingMoveToMM(-400)
	shaker.init()
	shaker.shake(42.6, 0.3)
	flow.init()
	flow.read()
	lastFrameWithColors = 0
	while lastFrameWithColors < 60:
		flow.read()
		if flow.getLastSum() == 0:
			lastFrameWithColors += 1
		else:
			lastFrameWithColors = 0
	flow.cleanup()
	shaker.cleanup()

def dump2():
	drive.blockingMoveToStockpile(1)
