#! /usr/bin/env python
#second file
from aubio import source, tempo
from numpy import median, diff
import queue as queue
import pyaudio
import wave

import threading

from multiprocessing.pool import ThreadPool
pool = ThreadPool(processes=2)

def read_from_file():
	with open("list.txt", "r") as ins:
		array = []
		for line in ins:
			array.append(int(line.strip()))
	return(array)

arr = list(reversed(read_from_file()))
print(arr)
def record(queue,num=1,name='recording.wav'):
	FORMAT = pyaudio.paInt16
	CHANNELS = 2
	RATE = 44100
	CHUNK = 1024
	RECORD_SECONDS = 4
	WAVE_OUTPUT_FILENAME = name
	 
	audio = pyaudio.PyAudio()
	 
	# start Recording
	stream = audio.open(format=FORMAT, channels=CHANNELS,
					rate=RATE, input=True,
					frames_per_buffer=CHUNK)
	#print("recording...")
	frames = []
	 
	for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
		data = stream.read(CHUNK)
		frames.append(data)
	#print("finished recording")
	 
	 
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

	
	if num < 4:
		r = threading.Thread(target=record, args=(queue,num+1))
		b = threading.Thread(target=get_file_bpm, args=(queue,))
		r.start()
		b.start()
		r.join()
	else:
		return queue
		#async_result = pool.apply_async(get_file_bpm)
		#recording = pool.apply_async(record, args=(num+1,))
		


def get_file_bpm(queue,params=None):
	""" Calculate the beats per minute (bpm) of a given file.
	    path: path to the file
	    param: dictionary of parameters
	"""
	path = '/Users/emilylepert/Documents/Olin_2/First_Semester/PoE/Final_Project/BeatDetection/recording.wav'
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
	#temp = queue.get()
	#total = int(temp)+len(beats)
	#print('beats stuff')
	#print(len(beats))
	queue.put(len(beats))
	#print(sum_up_Queue(queue))
	if len(arr) > 0:  
		if sum_up_Queue(queue) >= arr[-1]:
			arr.pop()
			print("Turn")


def sum_up_Queue(queue):
		tot = 0 
		for i in range(queue.qsize()):
			tot += queue.queue[i]
		return(tot)

if __name__ == '__main__':

	queue = queue.Queue()
	record(queue, num=1)
	print('done')