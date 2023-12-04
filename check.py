import wave
import numpy as np

# Assuming you have audio_data as your audio samples and sample_rate as the sample rate

sample_rate = 44100  # Replace with your actual sample rate
audio_data = np.zeros((sample_rate, 2))  # Replace with your actual audio data
# Specify the file path where you want to save the WAV file
file_path = "output.wav"

# Create a WAV file
with wave.open(file_path, 'w') as wave_file:
    wave_file.setnchannels(1)  # Mono audio
    wave_file.setsampwidth(2)  # 16-bit audio
    wave_file.setframerate(sample_rate)
    wave_file.writeframes(bytes(audio_data))

