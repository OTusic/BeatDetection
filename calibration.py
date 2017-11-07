#! /usr/bin/env python
# fist file
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

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
 
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

def record(queue,name='calibration.wav'):
	FORMAT = pyaudio.paInt16
	CHANNELS = 2
	RATE = 44100
	CHUNK = 1024
	RECORD_SECONDS = 20
	WAVE_OUTPUT_FILENAME = name
	 
	audio = pyaudio.PyAudio()
	 
	# start Recording
	stream = audio.open(format=FORMAT, channels=CHANNELS,
					rate=RATE, input=True,
					frames_per_buffer=CHUNK)
	print("recording...")
	frames = []
	 
	for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
		data = stream.read(CHUNK)
		frames.append(data)
	print("finished recording")
	 
	 
	# stop Recording
	stream.stop_stream()
	stream.close()
	audio.terminate()
	 
	waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
	waveFile.setnchannels(CHANNELS)
	waveFile.setsampwidth(audio.get_sample_size(FORMAT))
	waveFile.setframerate(RATE)
	waveFile.writeframes(b''.join(frames))
	waveFile.close()
	get_file_bpm(queue)


def get_file_bpm(queue, params=None):
	""" Calculate the beats per minute (bpm) of a given file.
	    path: path to the file
	    param: dictionary of parameters
	"""
	path = '/Users/emilylepert/Documents/Olin_2/First_Semester/PoE/Final_Project/BeatDetection/calibration.wav'
	if params is None:
		params = {}
	# default:
	samplerate, win_s, hop_s = 44100, 1024, 512
	if 'mode' in params:
		if params.mode in ['super-fast']:
			# super fast
			samplerate, win_s, hop_s = 4000, 128, 64
		elif params.mode in ['fast']:
			# fast
			samplerate, win_s, hop_s = 8000, 512, 128
		elif params.mode in ['default']:
			pass
		else:
			print("unknown mode {:s}".format(params.mode))
	# manual settings
	if 'samplerate' in params:
		samplerate = params.samplerate
	if 'win_s' in params:
		win_s = params.win_s
	if 'hop_s' in params:
		hop_s = params.hop_s
	

	s = source(path, samplerate, hop_s)
	samplerate = s.samplerate
	o = tempo("specdiff", win_s, hop_s, samplerate)
	# List of beats, in samples
	beats = []
	# Total number of frames read
	total_frames = 0

	while True:
		samples, read = s()
		is_beat = o(samples)
        
		if is_beat:
			this_beat = o.get_last_s()
			beats.append(this_beat)
            #if o.get_confidence() > .2 and len(beats) > 2.:
            #    break
		total_frames += read
		if read < hop_s:
			break
	queue.put(beats)
	return(beats)

def arduino_input(queue):

	# for mac
	cxn = Serial('/dev/tty.usbmodem1411', baudrate=9600)
	start = time.time()
	time_array = ['time']
	previous_entry = ''
	running = True
	while running==True:
		cxn.write([1])

		result = str(cxn.readline())

		if result[2:-5] == 'done':
			running = False
		elif result[2:-5] == 'turn':
			end = time.time()
			time_array.append(end-start)

	queue.put(time_array)

def dummy_input(queue):
	# for mac
	start = time.time()
	time_array = ['time']
	previous_entry = ''
	running = True
	while running==True:
		char = getch()
		if char == 'd':
			running = False

		elif char == 't':
			end = time.time()
			time_array.append(end-start)

	queue.put(time_array)
	calibrate(queue)


def start_calibrate():
	queuel = queue.Queue()
	pool = ThreadPool(processes=2)
	r = threading.Thread(target=record, args=(queuel,))
	b = threading.Thread(target=dummy_input, args=(queuel,))
	r.start()
	b.start()

def calibrate(queue):
	first = queue.queue[0]
	if first[0] == 'time':
		time_array = first[1:]
		beats = queue.queue[1]
	else:
		time_array = queue.queue[1][1:]
		beats = first

	calibrated = []
	for turn in time_array:
		print('interim beats')
		print(beats)
		for beat in range(len(beats)):
			if beats[beat] > turn:
				calibrated.append(len(beats[0:beat+1]))
				beats = beats[beat+1:]
				break
	print('beats')
	print(beats)
	print('turing')
	print(time_array)
	print('calibrated')
	print(calibrated)


if __name__ == '__main__':

	start_calibrate()
		


