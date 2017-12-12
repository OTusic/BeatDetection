'''
Code for calibrating page turning

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

def record(queue, amp_threshold=0.38):
	'''
	Records 60 seconds of music and detects when a beat is played
	Adapted and inspired from https://github.com/shunfu/python-beat-detector
	'''

	# SETUP
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

	#For each chunk of music recorded at one time
	for i in range(0, int(round(RATE / chunk * RECORD_SECONDS))):
		try:
			data = stream.read(chunk)
		except:
			continue
		stream.write(data, chunk)
		all_1.append(data)
		
		if len(all_1)>1:
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
				# do some math to find the amplitude of the chunk
				data = struct.unpack('<h', w.readframes(1))
				summ += (data[0]*data[0]) / 2
				if (j != 0 and (j % 1023) == 0):
					value = int(math.sqrt(summ / 1023.0) / 10)
					amps.append(value - delta)                
					summ = 0
					tarW=str(amps[0]*1.0/delta/100)
					
					# if the amplitude exceeds the threshold we've decided is a "beat"
					# "debouncing" beat detection with prev_value
					if abs(float(tarW)) > amp_threshold and prev_value < amp_threshold:
						print('tarW')
						print(tarW)
						beat_array_tracker(queue)

					prev_value = abs(float(tarW))
					delta = value
			all_1=[]
	
	print("done recording")

	stream.close()
	p.terminate()

	serr.close()

def beat_array_tracker(queue):
	'''
	Accesses the queue and increments the number of beats by 1
	'''
	
	for i in range(queue.qsize()):
		
		if queue.queue[i][0] == 'nbr_beats':
			beat_nbr = queue.queue[i][1:][0]
			beat_nbr += 1
			queue.queue.clear()
			queue.put(['nbr_beats', beat_nbr])
			break


def arduino_input(queue):
	'''
	Gets input from the Arduino via serial connection
	'''

	# for mac
	cxn = Serial('/dev/tty.usbmodem1421', baudrate=9600)

	running = True
	beat_array = []
	beat_nbr = 0
	while running==True:
		result = str(cxn.readline())
		print(result[2:])

		# writes to file the final beat array
		if result[2:-5] == 'done':

			running = False

			filename = "list.txt"
			file = open(filename, "w")
			for i in beat_array:
				writing = str(i[0])+'\n'
				file.write(writing)
			file.close()

		# stores the amount of beats played at that point into a list
		# resets the number of beats to 0
		elif result[2:-5] == 'turn':

			for i in range(queue.qsize()):
				
				if queue.queue[i][0] == 'nbr_beats':
					
					beat_nbr = queue.queue[i][1:]
					queue.queue.clear()
					queue.put(['nbr_beats', 0])
			beat_array.append(beat_nbr)

		# start recording
		elif result[2:-5] == 'stay':
			print('start')
			queue.put(['record'])

def start_calibrate():
	'''
	Starts the calibration process
	Starts a thread
	'''
	queuel = queue.Queue()
	queuel.put(['nbr_beats',0])
	print(queuel.qsize()) 
	b = threading.Thread(target=arduino_input, args=(queuel,))
	
	b.start()
	waiting = True
	# waits for the signal from the Arduino to start recording
	while waiting == True:
		for i in range(queuel.qsize()):
			if queuel.queue[i][0] == 'record':
				record(queuel)
				waiting = False


if __name__ == '__main__':

	start_calibrate()



