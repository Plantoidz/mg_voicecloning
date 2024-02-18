from pydub import AudioSegment, effects
from pydub.playback import play
from pydub.generators import Sine

class OtherworldlyAudio:
    def __init__(self, file_path):
        self.sound = AudioSegment.from_file(file_path, format="wav")

    def play_sound(self):
        play(self.sound)

    def pitch_shift(self, semitones= -10):
        self.sound = self.sound._spawn(self.sound.raw_data, overrides={
           "frame_rate": int(self.sound.frame_rate * (2 ** (semitones / 12.0)))
        }).set_frame_rate(self.sound.frame_rate)

    def apply_chorus(self, num_sounds=5, delay=500):
        chorus_sound = self.sound
        for _ in range(num_sounds):
            chorus_sound = chorus_sound.overlay(self.sound + delay)
            delay += 500
        self.sound = chorus_sound

    def apply_reverse(self):
        self.sound = self.sound.reverse()

    def apply_flanger(self, delay_time=5, decay_time=0.75):
        flanged = self.sound.flanger(delay=delay_time, decay=decay_time)
        self.sound = flanged

    def apply_reverb(self, num_echoes=3, start_delay=100, spacing_delay=100):
        reverb_sound = self.sound
        for _ in range(num_echoes):
            reverb_sound = reverb_sound.overlay(self.sound + start_delay, gain_during_overlay=0)
            start_delay += spacing_delay
        self.sound = reverb_sound


# Continue adding more methods for other effects as needed!

# mirror = OtherworldlyAudio("media/test.wav")
# mirror.pitch_shift()
# mirror.play_sound()