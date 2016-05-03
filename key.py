#!/usr/bin/env python
import sys

class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

getch = _GetchUnix()

def clamp(n, smallest, largest): return max(smallest, min(n, largest))

freq = 300
intensity = 50

while True:
	halfcycle = 5000000//freq
	high = halfcycle*intensity//100
	low = halfcycle-high
	print('f=' + str(freq/10) + 'Hz; intensity=' + str(intensity/100), file=sys.stderr)
	print(str(low) + ' ' + str(high))
	sys.stdout.flush()
	c = getch()
	if c == '\x03' or c == '\x04':
		break
	if c.lower() == 'a':
		freq -= 100
	if c.lower() == 's':
		freq -= 10
	if c.lower() == 'd':
		freq -= 1
	if c.lower() == 'f':
		freq += 1
	if c.lower() == 'g':
		freq += 10
	if c.lower() == 'h':
		freq += 100
	if c.lower() == 'y':
		intensity -= 10
	if c.lower() == 'x':
		intensity -= 1
	if c.lower() == 'c':
		intensity += 1
	if c.lower() == 'v':
		intensity += 10
	if c == '\x1b':
		d = getch()
		if ord(d) >= 64 and ord(d) <= 95:
			pass
		if d == '[':
			esq = ''
			while True:
				esq += getch()
				v = ord(esq[-1:])
				if v >= 64 and v <= 126:
					break
			(slow, fast, key) = (esq.startswith('1;2'), esq.startswith('1;5'), esq[-1:])
			factor = 1 if slow else 100 if fast else 10
			if key == 'A':
				intensity += factor
			if key == 'B':
				intensity -= factor
			if key == 'C':
				freq += factor
			if key == 'D':
				freq -= factor
		else:
			print('Invalid')
	print(ord(c))
	freq = clamp(freq, 20, 10000)
	intensity = clamp(intensity, 0, 99)

