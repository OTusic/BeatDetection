#! /usr/bin/env python
#second file
from aubio import source, tempo
from numpy import median, diff
import queue as queue
import pyaudio
import wave

import threading

from multiprocessing.pool import ThreadPool

def read_from_file():
	with open("list.txt", "r") as ins:
		array = []
		for line in ins:
			array.append(int(line.strip()))
	return(array)

arr = list(reversed(read_from_file()))

def record(name='recording.wav'):
	FORMAT = pyaudio.paInt16
	CHANNELS = 2
	RATE = 44100
	CHUNK = 1024
	RECORD_SECONDS = 10
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

	return get_file_bpm()

def get_file_bpm(params=None):
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

    def beats_to_bpm(beats, path):
        # if enough beats are found, convert to periods then to bpm
        if len(beats) > 1:
            if len(beats) < 4:
                print("few beats found in {:s}".format(path))
            bpms = 60./diff(beats)
            return median(bpms)
        else:
            print("not enough beats found in {:s}".format(path))
            return 0

    return beats_to_bpm(beats, path)

def trigger_turn(start,turns):
	
	j = len(turns) 
	while j>0:
		next_turn = turns[j]
		end = time.time()

		if end-start >= next_turn:
			print("Turn")
			j -= 1



if __name__ == '__main__':
	start = time.time()
	bpm = record()
	cur_bps = float(bpm)/60.0
	cal_bps = arr.pop()
	turn = []
	for i in range(len(arr)-1):
		turn.append(arr[i]*cur_bps)
	trigger_turn(start,turn)
	

