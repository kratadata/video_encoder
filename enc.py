#!/usr/bin/env python3

import argparse
import os
import cv2
import numpy as np
import soundfile
from PIL import Image
from scipy import signal
import json
import tempfile

width = 0
oversample = 0
lines = 0
pulse = 0
quiet = 0
frames_dir = ""
curr_dir = os.getcwd()
output_dir = curr_dir + "/outputs"

def encode(image, field):
	global width, oversample, lines, pulse, quiet
	image = image.resize((round(width * oversample), lines))
	image = image.convert('YCbCr')

	data = np.asarray(image)

	left = np.zeros(0)
	right = np.zeros(0)

	if field == 0:
		left = np.append(left, pulse * -1)
		right = np.append(right, pulse)

		left = np.append(left, pulse)
		right = np.append(right, pulse * -1)
	else:
		left = np.append(left, pulse)
		right = np.append(right, pulse * -1)

		left = np.append(left, pulse * -1)
		right = np.append(right, pulse)

	left = np.append(left, quiet)
	right = np.append(right, quiet)

	for line in range(0, data.shape[0] // 2):

		if line != 0:
			if line % 2 == 0:
				left = np.append(left, pulse)
				right = np.append(right, pulse)

				left = np.append(left, pulse * -1)
				right = np.append(right, pulse * -1)
			else:
				left = np.append(left, pulse * -1)
				right = np.append(right, pulse * -1)

				left = np.append(left, pulse)
				right = np.append(right, pulse)

			left = np.append(left, quiet)
			right = np.append(right, quiet)

		left = np.append(left, data[line * 2 + field, :, 0] / 255.0 - 0.5)

		if line % 2 == 0:

			right = np.append(
				right, data[line * 2 + field, :, 1] / 255.0 - 0.5)
		else:
			right = np.append(
				right, data[line * 2 + field, :, 2] / 255.0 - 0.5)

		left = np.append(left, quiet)
		right = np.append(right, quiet)

	left = signal.resample_poly(left, 1, oversample)
	right = signal.resample_poly(right, 1, oversample)

	return np.stack([left, right], 1)


def extract_image_one_fps(video_source_path):
	global frames_dir
	dir_path = os.path.dirname(os.path.realpath(video_source_path))
	frames_dir = dir_path + "/output_frames"

	os.makedirs(frames_dir, exist_ok=True)
	videocap = cv2.VideoCapture(video_source_path)
	count = 0
	success = True
	while success:
		videocap.set(cv2.CAP_PROP_POS_MSEC,(count*1000))
		success,image = videocap.read()

		## Stop when last frame is identified
		image_last = cv2.imread("frame{}.png".format(count-1))
		if np.array_equal(image,image_last):
			break

		cv2.imwrite(os.path.join(frames_dir, "frame%d.png" % count), image)     # save frame as PNG file
		print('{}.sec reading a new frame: {} '.format(count,success))
		count += 1



def video2audio(input, fps, ls, pl):
	global width, lines, oversample, frames_dir

	##extract_image_one_fps(input)

	sample_rate = 96000
	oversample = 10
	pulse_length = pl / 1000

	fps = fps
	lines = ls
	h_time = (1/fps/lines)*2
	width = h_time-(pulse_length*4)

	if width <= 0:
		print("Not time for image data, try reducing frame rate, lines, or pulse length.")
		exit(1)

	print("hFreq: {},".format(1.0/h_time))
	print("vFreq: {},".format(fps))
	print("overScan: {},".format(width/h_time))
	print("hOffset: {},".format((pulse_length*1.45)/h_time))
	print("pulseLength: {},".format(pulse_length))

	width *= sample_rate
	global pulse, quiet
	pulse = np.full(round(pulse_length * sample_rate * oversample), 1.0)
	quiet = np.zeros(round(pulse_length * sample_rate * oversample))

	file_name = os.path.splitext(os.path.basename(input[0]))[0] + ".wav"
	output_json = os.path.splitext(os.path.basename(input[0]))[0] + ".json"

	with open(os.path.join(output_dir, output_json), 'w') as json_file:
		info_data = {
			"hf": 1.0 / h_time,
			"vf": fps,
			"os": width / h_time,
			"hOffset": (pulse_length * 1.45) / h_time,
			"pl": pulse_length * 1.45
		}
		json.dump(info_data, json_file, indent=2)

	with soundfile.SoundFile(os.path.join(output_dir, file_name), 'w',  sample_rate, 2, 'FLOAT') as outFile:
		outFile.write(np.zeros((sample_rate, 2)))
		print("Encoding...")
		count = 0

		for imageFile in input:
			image = Image.open(imageFile)
			print("\rProcessing {}/{} frames".format(count+1, len(input)), end='')

			if count % 2 == 0:
				field = 0
			else:
				field = 1

			frame = encode(image, field)
			outFile.write(frame * 0.5)
			count += 1

			print("\nDone!")
			outFile.write(np.zeros((sample_rate, 2)))
