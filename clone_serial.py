from dotenv import load_dotenv
import os
import time
from simpleaichat import AIChat
from whisper_mic.whisper_mic import WhisperMic
from elevenlabs import clone, generate, stream, play, set_api_key
import speech_recognition as sr
from playsound import playsound
import random
from audio_effects import OtherworldlyAudio
import threading

import serial_utils
import serial.tools.list_ports

from serial_utils import send_to_arduino

import pygame

# Load environment variables from the .env file
load_dotenv()

#OPENAI / SIMPLEAICHAT
personality = open("doppelganger-psycho.txt").read().strip()
ai = AIChat(system=personality, api_key=os.environ.get("OPENAI"), model="gpt-4-1106-preview")

#WHISPER
mic = WhisperMic()

#ELEVENLABS
set_api_key(os.environ.get("ELEVEN"))
api_key = os.environ.get("ELEVEN")


# Load the sounds
beep_start = 'media/beep_start.mp3'
beep_stop = 'media/beep_stop.wav'
ambient_sounds = [
    'media/ambient1.mp3',
    'media/ambient2.mp3',
    'media/ambient3.mp3',
    'media/ambient4.mp3'
]
acknowledgement_sounds = [
    'media/acknowledgement1.mp3',
    'media/acknowledgement2.mp3',
    'media/acknowledgement3.mp3',
    'media/acknowledgement4.mp3'
]
radiation = random.choice(ambient_sounds)
acknowledgement = random.choice(acknowledgement_sounds)
ambient = random.choice(ambient_sounds)



def play_background_music(filename, loops=-1):
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play(loops)

def stop_background_music():
        print('stop background music')
        pygame.mixer.music.stop()


# set up serial communication
ports = serial.tools.list_ports.comports()
serial_ports = []
for port, desc, hwid in sorted(ports):
            print("{}: {} [{}]".format(port, desc, hwid))
            #if("USB" in desc): serial_ports.append(port)
            serial_ports.append(port)

print(serial_ports)

serial_connections = []
for sss in serial_ports:
        try:
            a = serial_utils.setup_serial(sss, 115200) 
            serial_connections.append( a )
            print("connected to: ", sss)
            send_to_arduino(a, "awake")
        except serial.SerialException:
             print(f"Failed to connect to {sss}")


def serial_msg_all(serials, msg):
    if(serials):
        for conn in serials:
            send_to_arduino(conn, msg)





def mirror_recording():
        mirror = OtherworldlyAudio(f"working/{timestamp}_recording.wav")
        time.sleep(3)
        mirror.pitch_shift()
        mirror.play_sound()



def main():
    counter = 0
    while True:
        playsound('media/beep_start.wav')

        serial_msg_all(serial_connections, "listening")

        utterance = mic.listen()

    #     try:
    #         with mic.source as microphone:
    #             audio = mic.recorder.listen(source=microphone)
            
    #         mic.__listen_handler()
    #    #     mic.__record_load(0, audio)
    #         audio_data = mic.__get_all_audio()


    #         utterance = mic.__transcribe(data=audio_data)
    #     except sr.WaitTimeoutError:
    #         mic.result_queue.put_nowait("Timeout: No speech detected within the specified time.")
    #     except sr.UnknownValueError:
    #         mic.result_queue.put_nowait("Speech recognition could not understand audio.")


        print(f"I heard: {utterance}")

        serial_msg_all(serial_connections, "thinking")
        play_background_music(ambient)


        # with open(f"working/{timestamp}_recording.wav", "wb") as f:
        #     f.write(utterance.get_wav_data())

        playsound(acknowledgement)
       # mirror_thread = threading.Thread(target=mirror_recording)
       # mirror_thread.start()

        # mirror_recording()

        response = ai(utterance)
        print(f"I said: {response}")
        counter += 1
        print(f"Interaction count: {counter}")
        audio_stream = generate(
            text=f"{response}",
            model="eleven_turbo_v2",
            voice=voice,
            stream=True
        )

        serial_msg_all(serial_connections, "speaking")
        stop_background_music()

        stream(audio_stream)

        serial_msg_all(serial_connections, "awake")


if __name__ == "__main__":


    # very dirty trick: we delete the last created voice by reading from the file
    filename = "last_voice.txt"
    if os.path.exists(filename):
        file = open(filename, "r")
        voice_id = file.readline().rstrip()
        file.close()    
      #  os.system(f"curl -X 'DELETE' 'https://api.elevenlabs.io/v1/voices/{voice_id}'  --header 'accept: application/json'  --header 'xi-api-key: {api_key}'")
      #  os.system(f"curl --request 'DELETE' --url 'https://api.elevenlabs.io/v1/voices/{voice_id}'  --header 'Content-Type: application/json'  --header 'xi-api-key: {api_key}'")
        print(f"curl -X 'DELETE' 'https://api.elevenlabs.io/v1/voices/{voice_id}'  --header 'accept: application/json'  --header 'xi-api-key: {api_key}'")
        os.system(f"curl -X 'DELETE' 'https://api.elevenlabs.io/v1/voices/{voice_id}'  --header 'accept: application/json'  --header 'xi-api-key: {api_key}'")


    timestamp = str(int(time.time()))
    print(timestamp)

    # audio = generate(text="OK, we're ready to go. Please introduce yourself in a few sentences.")
    playsound(beep_start)

    serial_msg_all(serial_connections, "listening")

    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("\n\nI'm listening...")
        audio = r.listen(source)
        with open(f"working/{timestamp}_recording.wav", "wb") as f:
            f.write(audio.get_wav_data())

    serial_msg_all(serial_connections, "thinking")
    play_background_music(ambient)

    voice = clone(
        name=f"{timestamp}",
        description="Testing", # Optional
        files=[f"working/{timestamp}_recording.wav"],
    )

    print(voice)

    audio = generate(text="Great - such a pleasure to have a little chat with you. What is a thought that you cannot let go of?", voice=voice)
    
    serial_msg_all(serial_connections, "speaking")
    stop_background_music()
    play(audio)

    # dirty trick to delete the voice after the ongoing loop.
    voice_id = voice.voice_id
    # voice_name = voice.name
    # print("voice_id to be deleted === ", voice_id, "  with name = ", voice_name)
    file = open("last_voice.txt", "w+")
    file.write(voice_id)
    file.close()

    main()

