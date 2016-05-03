#!/usr/bin/env python

import shaker
import time

shaker.init()

while(True):
	shaker.shake(800,0.9)
	time.sleep(0.4)
	shaker.shake(600,0.9)
	time.sleep(0.4)

for i in range(300,500):
	shaker.shake(i, 0.9)
	time.sleep(0.001)

shaker.cleanup()
