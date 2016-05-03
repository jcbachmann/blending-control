#!/usr/bin/env python

import time
import drive
import shaker

shaker.init()
drive.init()

drive.read()
drive.read()
drive.read()
drive.read()
drive.read()

pos = drive.getPosInMM()

while True:
	shaker.shake(400, 0.8)
	drive.moveToMM(pos)
	time.sleep(0.5)
	shaker.stop()
	pos += 2
	drive.poll()
	drive.poll()
	time.sleep(0.5)
