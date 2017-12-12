'''
Code for live music playing

Authors: Tusic
'''

import queue
import pyaudio
import wave
import threading
import sys, termios, tty, os, time
import struct
import math

from serial import Serial, SerialException

cxn = Serial('/dev/tty.usbmodem1421', baudrate=9600)

def read_from_file():
	'''
	reads from the file with the calibration data
	'''
	with open("list.txt", "r") as ins:
		array = []
		for line in ins:
			array.append(int(line.strip()))
	return(array)

arr = list(read_from_file())

def record(queue, amp_threshold=0.4):
	'''
	Records 60 seconds of music and detects when a beat is played
	Adapted and inspired from https://github.com/shunfu/python-beat-detector
	'''
	chunk = 1024
	FORMAT = pyaudio.paInt16
	CHANNELS = 1
	RATE = 44100
	RECORD_SECONDS = 60
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
	serr.close()


def beat_array_tracker(queue):

	for i in range(queue.qsize()):

		# checks if the current beat number is equal to
		# the one in the file
		if queue.queue[i][0] == 'nbr_beats':
			beat_nbr = queue.queue[i][1:][0]
			if arr:
				# if so turn the page and remove element from
				# calibration list
				if beat_nbr >= arr[0]:
					turn_page()
					beat_nbr = 0
					arr.pop(0)
				# if not, increment by one
				else:
					beat_nbr += 1
			else:
				beat_nbr += 1

			queue.queue.clear()
			queue.put(['nbr_beats', beat_nbr])
			break

def turn_page():
	'''
	sends signal to Arduino to turn page
	'''
	cxn.write([1])

def arduino_start(queue):
	'''
	Gets input from the Arduino via serial connection
	'''

	running = True
	while running==True:

		result = str(cxn.readline())
		print(result[2:])
		# checks to see that player wants to start playing
		if result[2:7] == 'start':
			print('start')
			queue.put(['record'])
			running = False

def start_live_run():
	'''
	starts process for live playing
	'''
	queuel = queue.Queue()
	queuel.put(['nbr_beats',0])
	print(queuel.qsize()) 
	pool = ThreadPool(processes=2)

	b = threading.Thread(target=arduino_start, args=(queuel,))
	
	b.start()
	waiting = True
	while waiting == True:
		for i in range(queuel.qsize()):
			if queuel.queue[i][0] == 'record':
				record(queuel)
				waiting = False

if __name__ == '__main__':
	start_live_run()
