import sys
import struct
import socket
import errno
import time

conn = None
dgram = b''
pos = 0
pending = dict()
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
	initReq()

def send(instruction, type, value):
	global conn
	global pending
	if instruction in pending and time.time() < pending[instruction] + 0.2:
		#print('Already pending')
		return
	pending[instruction] = time.time()
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
	send(4, 0, round(value * stockpileLength))

def moveToMM(value):
	send(4, 0, round(value * mmLength))

def poll():
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
	initReq()

def parse(dgram):
	global pending
	global pos
	if sum(dgram[:8]) % 256 != dgram[8]:
		raise IOError('wrong serial checksum')
	
	(address, target, status, instruction, value) = struct.unpack('>BBBBix', dgram)

	if instruction in pending:
		pending.pop(instruction)

	if instruction == get_coordinate:
		pos = value
		initReq()
		
def initReq():
	send(capture_coordinate, 1, 0)
	send(get_coordinate, 1, 0)

def getPosInStockpile():
	global pos
	return pos / stockpileLength

def getPosInMM():
	global pos
	return pos / mmLength

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
