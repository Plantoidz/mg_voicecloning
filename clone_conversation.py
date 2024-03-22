from dotenv import load_dotenv
import os
import time
import sys
from simpleaichat import AIChat
from whisper_mic.whisper_mic import WhisperMic
from elevenlabs import clone, generate, stream, save, play, set_api_key
import speech_recognition as sr
from playsound import playsound
import random
from audio_effects import OtherworldlyAudio
import threading

# import serial_utils
# import serial.tools.list_ports

# from serial_utils import send_to_arduino

import pygame

# Load environment variables from the .env file
load_dotenv()


#WHISPER
mic = WhisperMic()

#ELEVENLABS
set_api_key(os.environ.get("ELEVEN"))
api_key = os.environ.get("ELEVEN")


# Load the sounds
beep_start = 'media/beep_start_real.mp3'
beep_stop = 'media/beep_stop.wav'

ambient_sounds = [
    'media/ambient1.mp3',
    'media/ambient2.mp3',
    'media/ambient3.mp3',
    'media/ambient4.mp3',
    'media/AMBIENT5.mp3',
    'media/AMBIENT6.mp3',
    'media/AMBIENT7.mp3',
]
acknowledgement_sounds = [
    'media/acknowledgement1.mp3',
    'media/acknowledgement2.mp3',
    'media/acknowledgement3.mp3',
    'media/acknowledgement4.mp3'
]
radiation = random.choice(ambient_sounds)
acknowledgement = random.choice(acknowledgement_sounds)

counter = 0


def play_background_music(filename, loops=-1):
        pygame.mixer.init()
        pygame.mixer.music.load(filename)
        pygame.mixer.music.play(loops)

def stop_background_music():
        print('stop background music')
        pygame.mixer.music.fadeout(1000)



def main(wavfile):


        if(wavfile):
             # use the audio file as the audio source
            r = sr.Recognizer()
            with sr.AudioFile(wavfile) as source:
                audio = r.record(source)  # read the entire audio file
                utterance = r.recognize_google(audio)

        else:
            playsound(beep_start)
            utterance = mic.listen()
        

        print(f"I heard: {utterance}")


        play_background_music(radiation)
        playsound(acknowledgement)

        response = ai(utterance)
        print(f"I said: {response}")

        global counter
        counter += 1
        print(f"Interaction count: {counter}")

        audio_stream = generate(
            text=f"{response}",
            model="eleven_turbo_v2",
            voice=voice,
            stream=False
        )

        stop_background_music()

       # play(audio_stream)
        save(audio_stream, "myoutput.mp3")

        with open(context_prompt, "a") as myfile:
            myfile.write(f"[Your parallel self]: {utterance}\n")
            myfile.write(f"[You]: {response}\n")






def parallel_self(context_prompt, voice_id):

    # very dirty trick: we delete the last created voice by reading from the file
    filename = "last_voice.txt"
    if os.path.exists(filename):
        file = open(filename, "r")
        ex_voice = file.readline().rstrip()
        file.close()    
        print(f"curl -X 'DELETE' 'https://api.elevenlabs.io/v1/voices/{ex_voice}'  --header 'accept: application/json'  --header 'xi-api-key: {api_key}'")
        os.system(f"curl -X 'DELETE' 'https://api.elevenlabs.io/v1/voices/{ex_voice}'  --header 'accept: application/json'  --header 'xi-api-key: {api_key}'")


    #OPENAI / SIMPLEAICHAT
    personality = open(context_prompt).read().strip()
    ai = AIChat(system=personality, api_key=os.environ.get("OPENAI"), model="gpt-4-1106-preview")

    playsound(beep_start)

    if(not voice_id):  ## Create a new voice
         
        timestamp = str(int(time.time()))
        print(timestamp)

        r = sr.Recognizer()
        with sr.Microphone() as source:
            print("\n\nI'm listening...")
            audio = r.listen(source)
            print("here")
            utterance = r.recognize_google(audio)
            print("there")

            with open(f"working/{timestamp}_recording.wav", "wb") as f:
                f.write(audio.get_wav_data())

        play_background_music(radiation)

        voice = clone(
                name=f"{timestamp}",
                description="Testing", # Optional
                files=[f"working/{timestamp}_recording.wav"],
        )
        # audio = generate(text="Great - such a pleasure to have a little chat with you. What is a thought that you cannot let go of?", voice=voice)
        print(voice)

        # dirty trick to record the voice in a file in order to delete the voice after the next launch of the software.
        voice_id = voice.voice_id
        file = open("last_voice.txt", "w+")
        file.write(voice_id)
        file.close() 
    

        # use the audio file as the audio source
        # z = sr.Recognizer()
        # with sr.AudioFile(f"working/{timestamp}_recording.wav") as source:
        #         z.adjust_for_ambient_noise(source)
        #         audio = z.record(source)  # read the entire audio file
                # utterance = z.recognize_google(audio)
 
    else:
         
        utterance = mic.listen()

    print(f"I heard: {utterance}")


    play_background_music(radiation)
    playsound(acknowledgement)

    response = ai(utterance)
    print(f"I said: {response}")

    global counter
    counter += 1
    print(f"Interaction count: {counter}")

    audio_stream = generate(
            text=f"{response}",
            model="eleven_turbo_v2",
            voice=voice_id,
            stream=False
    )

    stop_background_music()

    # play(audio_stream)
    save(audio_stream, "myoutput.mp3")

    with open(context_prompt, "a") as myfile:
            myfile.write(f"[Your parallel self]: {utterance}\n")
            myfile.write(f"[You]: {response}\n")


    return("myoutput.mp3", voice_id)




 ## TODO: 
## input is (context, voice_id)
## output is (audiofile, voice_id)


if __name__ == "__main__":
    
    voice_id = None

    while True:
        (responsefile, voice_id) = parallel_self(sys.argv[1] or "doppelganger-pyscho.txt", voice_id)
        playsound(responsefile)


