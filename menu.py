#!/usr/bin/env python

import subprocess
import os
import stacker
import dump_feeder
import reclaimer
import drive
import shaker
import time

run = True
lastStockpileName = "unknown"
options = [
#--- stockpile
["stack", lambda: stackFile()],
["dump feeder material", lambda: dump_feeder.dump1()],
["flush feeder material", lambda: dump_feeder.dump2()],
["reclaim", lambda: reclaimer.reclaim("../data/" + lastStockpileName)],
#--- feeder
["control feeder", "./shakekey.sh"],
["stop feeder", lambda: shaker.stop()],
#--- drive
["flush stockpile",  lambda: drive.flush()],
["drive to start pos", lambda: drive.moveToStockpile(0)],
["drive to end pos", lambda: drive.moveToStockpile(1)],
["drive to dump pos", lambda: drive.moveToMM(-400)],
["drive left", lambda: drive.run(-1000)],
["drive right", lambda: drive.run(1000)],
["drive stop", lambda: drive.stop()],
#--- other
["colorcount", lambda: os.system("colorcount")],
["alarm", "./alarm.sh"],
["poweroff", lambda: os.system("poweroff")],
["reboot", lambda: os.system("reboot")],
["close", lambda: stop()]
]

def stop():
	global run
	run = False
	return 0
	
def stackFile():
	global lastStockpileName
	print("\nStockpiles:")
	directoryFiles = os.listdir("../data")
	directoryFiles = sorted(list(filter(lambda x: x.endswith(".stockpile"), directoryFiles)))
	stockpileNum = 0
	for file in directoryFiles:
		stockpileNum += 1
		print(str(stockpileNum) + " - " + file)
	print(str(stockpileNum + 1) + " - return")
	choiceIndex = int(input("Choose your stockpile...\n"))
	if(choiceIndex == stockpileNum + 1):
		return 0
	else:
		lastStockpileName = directoryFiles[choiceIndex - 1]
	print(lastStockpileName)
	stacker.stack("../data/" + lastStockpileName)	
	return 0
	
def printTopic(topic):
	print("--- " + topic + " ---")
	return 0
	
def showMenu():
	#print list
	index = 0
	printTopic("stockpile")
	for option in options:
		index += 1
		if(index == 5): printTopic("feeder")
		if(index == 7): printTopic("drive")
		if(index == 14): printTopic("other")
		print(str(index) + " - " + option[0])
	print("\n")
	response = int(input("Choose your choice...\n")) - 1
	os.system("cowsay " + str(options[response][0]))
	
	#execute
	program = options[response][1]
	if(isinstance(program, str)):
		os.system(program)
	else:
		drive.poll()
		program()
	os.system("sync")

drive.init()
while(run):
	showMenu()
drive.cleanup()
