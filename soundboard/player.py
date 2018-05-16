import pygame
import pyaudio
import wave

pygame.mixer.init()

p = pyaudio.PyAudio()
chunk = 1024
device = p.get_default_output_device_info()["name"]

USE_PYAUDIO = input("Use additional device for WAV files? (y/n): ") == "y"
if USE_PYAUDIO:
    print()
    for x in range(20):
        try:
            device = p.get_device_info_by_index(x)
            if device["maxOutputChannels"] > 0:
                print("{} - {}".format(x, device["name"]))
        except OSError:
            pass
            
    device = int(input("\nDevice number: "))
    
sounds = {}

def load(path):
    pass

def play(path):
    try:
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        print("Played file '{}'.".format(path))
    except:
        print("Failed to play file '{}' as sound.".format(path))
        
    if USE_PYAUDIO and path.endswith(".wav"):
        sound = wave.open(path, "rb")
        stream = p.open(format=p.get_format_from_width(sound.getsampwidth()),
                        channels=sound.getnchannels(),
                        rate=sound.getframerate(),
                        output_device_index=device,
                        output=True)
        data = sound.readframes(chunk)
        while len(data) > 0:
            stream.write(data)
            data = sound.readframes(chunk)
        stream.stop_stream()
        stream.close()
        sound.close()
