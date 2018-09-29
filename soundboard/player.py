import pygame
import pyaudio
import wave
from threading import Thread

pygame.mixer.init()

p = pyaudio.PyAudio()
chunk = 1024
default_device = p.get_default_output_device_info()["index"]
mirror_device = None

USE_PYAUDIO = input("Use additional device for WAV files? (y/n): ") == "y"
if USE_PYAUDIO:
    print()
    for x in range(20):
        try:
            device = p.get_device_info_by_index(x)
            if device["maxOutputChannels"] > 0:
                print("{} - {}".format(x, device["name"]) + (" <- default" if x == default_device else ""))
        except OSError:
            pass
            
    mirror_device = int(input("\nDevice number: "))
    
sounds = {}

def load(path):
    pass

queue = []

def add_to_queue(path):
    global queue
    queue.append(path)

def play_queue():
    global queue
    if len(queue) == 1:
        play_async(queue[0])
    else:
        for path in queue:
            play(path)
    queue = []

def play(path, output_device=None, volume=1):

    if not USE_PYAUDIO or not path.endswith(".wav"):
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
            print("playing file '{}' with pygame.".format(path))
        except:
            print("Failed to play file '{}' with pygame.".format(path))
    
    elif USE_PYAUDIO:

        if output_device is None:
            output_device = default_device
        
        print("Playing file '{}' on device {}.".format(path, output_device))

        if output_device != mirror_device:
            play_async(path, output_device=mirror_device)
        
        sound = wave.open(path, "rb")
        stream = p.open(format=p.get_format_from_width(sound.getsampwidth()),
                        channels=sound.getnchannels(),
                        rate=sound.getframerate(),
                        output_device_index=output_device,
                        output=True)
        data = sound.readframes(chunk)
        while len(data) > 0:
            stream.write(data)
            data = sound.readframes(chunk)
        stream.stop_stream()
        stream.close()
        sound.close()

def play_async(path, output_device=None, volume=1):
    thread = Thread(target=play, args=(path,output_device, volume))
    thread.start()
    return thread

