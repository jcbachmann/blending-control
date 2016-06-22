import sys
import struct
import socket
import errno
import time

conn = None
dgram = b''
pos = 0
startingPosMM = 450
pending = dict()
issued = dict()
lastPending = 0
stockpileLength = 550000
mmLength = 500000/635

get_coordinate = 31
capture_coordinate = 32

def init():
	global conn
	conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	conn.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
	conn.connect(("192.168.178.29", 54321))
	conn.setblocking(0)
	sendCaptureAndGetCommand()

def send(instruction, type, value):
	global conn
	global pending
	global issued
	global lastPending
	#if time.time() < lastPending + 1.0:
	#	print('Already lastPending ', instruction)
	#	return
	lastPending = time.time()
	if instruction in pending and time.time() < pending[instruction] + 0.2:
		print('Already pending ', instruction)
		return
	print('Sent ', instruction)
	pending[instruction] = time.time()
	issued[instruction] = time.time()
	address = 1
	motor = 0
	dgram = struct.pack('>BBBBi', address, instruction, type, motor, value)
	dgram += struct.pack('>B', sum(bytearray(dgram)) % 256)
	conn.sendall(dgram)

def run(speed):
	if (speed > 0):
		send(1, 0, speed)
	else:
		send(2, 0, -speed)

def stop():
	send(3, 0, 0)

def moveToStockpile(value):
	global startingPos
	send(4, 0, round(startingPosMM * mmLength + value * stockpileLength))

def moveToMM(value):
	send(4, 0, round((value + startingPosMM) * mmLength))

def pollWithoutCapture():
	global conn
	global dgram
	try:
		while True:
			dgram += conn.recv(9 - len(dgram))
			if len(dgram) == 9:
				parse(dgram)
				dgram = b''
	except BlockingIOError:
		pass

def poll():
	pollWithoutCapture()
	sendCaptureAndGetCommand()

def parse(dgram):
	global pending
	global issued
	global pos
	global lastPending
	if sum(dgram[:8]) % 256 != dgram[8]:
		raise IOError('wrong serial checksum')
	
	(address, target, status, instruction, value) = struct.unpack('>BBBBix', dgram)

	if instruction in pending:
		pending.pop(instruction)
		lastPending = 0

	if instruction == get_coordinate:
		pos = value
		sendCaptureAndGetCommand()
		
def sendCaptureAndGetCommand():
	if capture_coordinate not in issued or time.time() > issued[capture_coordinate] + 0.2:
		send(capture_coordinate, 1, 0)
	if get_coordinate not in issued or time.time() > issued[get_coordinate] + 0.2:
		send(get_coordinate, 1, 0)

def getPosInStockpile():
	global pos
	return (pos - startingPosMM * mmLength) / stockpileLength

def getPosInMM():
	global pos
	return (pos / mmLength) - startingPosMM

def blockingMoveToStockpile(pos):
	poll()
	moveToStockpile(pos)
	while True:
		time.sleep(0.1)
		poll()
		print("stockpile part left: " + str(abs(getPosInStockpile() - pos)))
		if abs(getPosInStockpile() - pos) < 0.02:
			break

def blockingMoveToMM(pos):
	poll()
	moveToMM(pos)
	while True:
		time.sleep(0.1)
		poll()
		print("mm left: " + str(abs(getPosInMM() - pos)))
		if abs(getPosInMM() - pos) < 1:
			break

def showStockpilePosInLoop():
	while True:
		time.sleep(0.1)
		poll()
		print("stockpile part: " + str(getPosInStockpile()))

def showMMPosInLoop():
	while True:
		time.sleep(0.1)
		poll()
		print("mm: " + str(getPosInMM()))

def flush():
	run(2047)
	while True:
		time.sleep(0.1)
		poll()
		if getPosInStockpile() > 2.2:
			break
	run(-2047)
	while True:
		time.sleep(0.1)
		poll()
		if getPosInStockpile() < 0.05:
			break
	blockingMoveToStockpile(0)

def cleanup():
	global conn
	conn.shutdown(1)
	conn.close()
