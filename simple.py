from simpleaichat import AIChat
from whisper_mic.whisper_mic import WhisperMic
from elevenlabs import generate, stream, set_api_key
from playsound import playsound

#OPENAI / SIMPLEAICHAT
personality = open("glitch3.txt").read().strip()
ai = AIChat(system=personality, api_key="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", model="gpt-4-1106-preview")

#WHISPER
mic = WhisperMic()

#ELEVENLABS
set_api_key("7392d8c1aed03a77decf691927128ba3")

def main():
	counter = 0
	while True:
		playsound('media/beep_start.wav')
		utterance = mic.listen()
		print(f"I heard: {utterance}")
		response = ai(utterance)
		print(f"I said: {response}")
		counter += 1
		print(f"Interaction count: {counter}")
		audio_stream = generate(
		    text=f"{response}",
		    model="eleven_multilingual_v2",
		    voice="o7lPjDgzlF8ZloHzVPeK",
			stream=True
#			stream=False
		)
		stream(audio_stream)

if __name__ == "__main__":
    main()
