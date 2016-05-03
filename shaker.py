import subprocess
import time

shakedma = None

def init():
	global shakedma
	shakedma = subprocess.Popen(["shakedma"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)

def shake(freq, intensity):
	global shakedma
	halfcycle = 500000/freq
	high = halfcycle*intensity
	low = halfcycle-high
	shakedma.stdin.write((str(round(low)) + ' ' + str(round(high)) + '\n').encode('utf-8'))
#	print((str(round(low)) + ' ' + str(round(high)) + '\n'))
	shakedma.stdin.flush()

def stop():
	global shakedma
	shakedma.stdin.write("100 0\n".encode('utf-8'))
	shakedma.stdin.flush()

def cleanup():
	global shakedma
	shakedma.terminate()
	shakedma.wait()
