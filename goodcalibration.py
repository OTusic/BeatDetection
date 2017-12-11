from aubio import source, tempo
from numpy import median, diff
import queue
import pyaudio
import wave
import time
import threading

from pynput import keyboard

from multiprocessing.pool import ThreadPool

from serial import Serial, SerialException

import sys, termios, tty, os, time

import struct
import math


def getch():
	fd = sys.stdin.fileno()
	old_settings = termios.tcgetattr(fd)
	try:
		tty.setraw(sys.stdin.fileno())
		ch = sys.stdin.read(1)
 
	finally:
		termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
	return ch

def record(queue, amp_threshold=0.4):
	#serr=serial.Serial('/dev/cu.usbmodem1411', baudrate=9600)
	chunk = 1024
	FORMAT = pyaudio.paInt16
	CHANNELS = 1
	RATE = 44100
	RECORD_SECONDS = 50
	WAVE_OUTPUT_FILENAME = "output.wav"

	p = pyaudio.PyAudio()

	stream = p.open(format = FORMAT,
					channels = CHANNELS,
					rate = RATE,
					input = True,
					output = True,
					frames_per_buffer = chunk)

	print("* recording")
	maxNormal=1
	prevVals=[0,255]
	prev=0
	all_1 = []
	prev_value = 0
	for i in range(0, int(round(RATE / chunk * RECORD_SECONDS))):
		try:
			data = stream.read(chunk)
		except:
			continue
		stream.write(data, chunk)
		all_1.append(data)
		if len(all_1)>1:
			#data = ''.join(all_1)
			wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
			wf.setnchannels(CHANNELS)
			wf.setsampwidth(p.get_sample_size(FORMAT))
			wf.setframerate(RATE)
			wf.writeframes(data)
			wf.close()
			w = wave.open(WAVE_OUTPUT_FILENAME, 'rb')
			summ = 0
			value = 1
			delta = 1
			amps = [ ]
			for j in range(0, w.getnframes()):
				data = struct.unpack('<h', w.readframes(1))
				summ += (data[0]*data[0]) / 2
				if (j != 0 and (j % 1023) == 0):
					value = int(math.sqrt(summ / 1023.0) / 10)
					amps.append(value - delta)                
					summ = 0
					tarW=str(amps[0]*1.0/delta/100)
					#ser.write(tarW)
					
					if abs(float(tarW)) > amp_threshold and prev_value < amp_threshold:
						print('tarW')
						print(tarW)
						beat_array_tracker(queue)
					prev_value = abs(float(tarW))
					delta = value
			all_1=[]
	print("this should never print")

	stream.close()
	p.terminate()

	# write data to WAVE file
	#data = ''.join(all_1)
	wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
	wf.setnchannels(CHANNELS)
	wf.setsampwidth(p.get_sample_size(FORMAT))
	wf.setframerate(RATE)
	wf.writeframes(data)
	wf.close()
	serr.close()

def beat_array_tracker(queue):
	print(queue.qsize())
	for i in range(queue.qsize()):
		print(queue.queue[i])
		if queue.queue[i][0] == 'nbr_beats':
			beat_nbr = queue.queue[i][1:][0]
			print('beat_nbr')
			print(beat_nbr)
			beat_nbr += 1
			queue.queue.clear()
			queue.put(['nbr_beats', beat_nbr])
			break


def arduino_input(queue):

	# for mac
	cxn = Serial('/dev/tty.usbmodem1411', baudrate=9600)
	start = time.time()
	time_array = ['time']
	previous_entry = ''
	running = True
	beat_array = []
	beat_nbr = 0
	while running==True:
		#cxn.write([1])

		result = str(cxn.readline())
		print(result[2:])
		if result[2:-5] == 'done':
			running = False

			filename = "list.txt"
			file = open(filename, "w")
			for i in beat_array:
				writing = str(i[0])+'\n'
				file.write(writing)
			file.close()

		elif result[2:-5] == 'turn':

			for i in range(queue.qsize()):
				
				if queue.queue[i][0] == 'nbr_beats':
					
					beat_nbr = queue.queue[i][1:]
					queue.queue.clear()
					queue.put(['nbr_beats', 0])
			beat_array.append(beat_nbr)
		elif result[2:-5] == 'stay':
			print('start')
			queue.put(['record'])

def dummy_input(queue):
	# for mac
	start = time.time()
	time_array = ['time']
	previous_entry = ''
	running = True
	beat_array = []
	beat_nbr = 0
	while running==True:
		char = getch()
		if char == 'd':
			running = False

			filename = "list.txt"
			file = open(filename, "w")
			for i in beat_array:
				writing = str(i[0])+'\n'
				file.write(writing)
			file.close()

		elif char == 't':
			for i in range(queue.qsize()):
				
				if queue.queue[i][0] == 'nbr_beats':
					
					beat_nbr = queue.queue[i][1:]
					queue.queue.clear()
					queue.put(['nbr_beats', 0])
			beat_array.append(beat_nbr)
		elif char == 's':
			print('start')
			queue.put(['record'])

def start_calibrate():
	queuel = queue.Queue()
	queuel.put(['nbr_beats',0])
	print(queuel.qsize()) 
	pool = ThreadPool(processes=2)
	b = threading.Thread(target=arduino_input, args=(queuel,))
	
	b.start()
	waiting = True
	while waiting == True:
		for i in range(queuel.qsize()):
			if queuel.queue[i][0] == 'record':
				record(queuel)
				waiting = False


if __name__ == '__main__':

	start_calibrate()


