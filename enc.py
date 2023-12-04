#!/usr/bin/env python3

import argparse
import os
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

def video2audio(inputs, fps, ls, pl):

	# parser.add_argument('-i', '--input', required=True, action='append', dest='inputs', help='input file pattern(s)', type=str )
	#parser.add_argument('outfile', type=argparse.FileType( 'wb' ) )

	#parser.add_argument('-r', '--rate', dest='rate', action='store', help='sample rate', default=c, type=int)
	#parser.add_argument('-f', '--fps', dest='fps', action='store', help='frames per second', default=3, type=float)
	#parser.add_argument('-l', '--lines', dest='lines', action='store', help='lines of resolution', default=150, type=int)
	#parser.add_argument('-p', '--pulselength', dest='pulselength', action='store', help='length of sync pulses in ms', default=0.2, type=float)
	#parser.add_argument('-o', '--oversample', dest='oversample', action='store', help='oversampling amount', default=10, type=int)

	#args = parser.parse_args()
	global width, lines, oversample

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

	file_name = os.path.splitext(os.path.basename(inputs[0]))[0] + ".wav"
	output_json = os.path.splitext(os.path.basename(inputs[0]))[0] + ".json"

	with open(output_json, 'w') as json_file:
		info_data = {
			"hf": 1.0 / h_time,
			"vf": fps,
			"os": width / h_time,
			"hOffset": (pulse_length * 1.45) / h_time,
			"pl": pulse_length * 1.45
		}
		json.dump(info_data, json_file, indent=2)

	with soundfile.SoundFile(file_name, 'w',  sample_rate, 2, 'FLOAT') as outFile:
		outFile.write(np.zeros((sample_rate, 2)))
		print("Encoding...")
		count = 0

		for imageFile in inputs:
			image = Image.open(imageFile)
			print("\rProcessing {}/{} frames".format(count+1, len(inputs)), end='')

			if count % 2 == 0:
					field = 0
			else:
				field = 1

			frame = encode(image, field)
			outFile.write(frame * 0.5)
			count += 1

			print("\nDone!")
			outFile.write(np.zeros((sample_rate, 2)))
