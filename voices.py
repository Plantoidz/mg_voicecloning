import os
import sys
from elevenlabs import voices, generate, set_api_key

api_key = "7392d8c1aed03a77decf691927128ba3"
set_api_key("7392d8c1aed03a77decf691927128ba3")

voices = voices()
audio = generate(text="Hello there!", voice=voices[0])
for v in voices:
	print(v, "\n")
print("total voices: ", len(voices))

if(len(sys.argv) > 1):
	voice_id = sys.argv[1] 
	if(voice_id):
		print(f"curl -X 'DELETE' 'https://api.elevenlabs.io/v1/voices/{voice_id}'  --header 'accept: application/json'  --header 'xi-api-key: {api_key}'")
		os.system(f"curl -X 'DELETE' 'https://api.elevenlabs.io/v1/voices/{voice_id}'  --header 'accept: application/json'  --header 'xi-api-key: {api_key}'")

