#harpoon - a midi thing
import board
import random
import time

import usb_midi
import adafruit_midi
from adafruit_midi.control_change import ControlChange
from adafruit_midi.note_off import NoteOff
from adafruit_midi.note_on import NoteOn
from adafruit_midi.start import Start
from adafruit_midi.stop import Stop

import remidi
import neopixel

np = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.1)

class Sequencer():
    def __init__(self, bpm, v, scale):
        self.bpm = bpm
        self.v = v
        self.beat = 60/bpm * v
        self.scale = scale
        self.next = time.monotonic()+self.beat
        self.playing = False
        self.drift = 0
        self.rythm = [3,1,2,1,1]

    def on(self, riff):
        self.step = 0
        self.riff = riff
        return self

    def advance(self):
        now = time.monotonic()
        if not self.playing: return 0
        if now < self.next: return 1
        rstep = self.step % len(self.rythm)
        self.next = now+self.beat*self.rythm[rstep]
        step = self.step % len(self.riff)
        note = self.riff[step]
        if self.drift > random.random():
            self.riff[step] = random.choice(self.scale)
        self.step += 1
        return note

    def set_tempo(self, n):
        if n < 10:
            print(f"Invalid tempo: {n}")
        else:
            self.bpm = n
            self.beat = 60/n * self.v
        return self.bpm

    def set_root(self, n):
        if 20 < n < 68:
            self.scale = remidi.natural(n)

    def start(self):
        self.step = 0
        self.playing = True

    def stop(self):
        self.playing = False

#riff = [49, 61, 56, 45, 57, 62, 50, 62, 56, 52, 59, 56, 52, 59, 61, 45]
scale = remidi.natural(26)
riff = [random.choice(scale) for _ in range(8)]
seq = Sequencer(bpm=20,v=1/8, scale=scale).on(riff)
seq.playing = True
seq.drift = 0.1

# No MIDI? Want a stand-alone player?
# Connect a small speaker to pin D12 (and ground),
# then use PWMOut to play the tones.

#from pwmio import PWMOut
#dac = PWMOut(board.D12, duty_cycle=0, frequency=440, variable_frequency=True)
#slope=0.91
def pwm_out():
    note = seq.advance()
    if note == 0:
        dac.duty_cycle=0
    if note > 20:
        dac.frequency=int(remidi.frequency(note))
        dac.duty_cycle=0x0800
    dac.duty_cycle = int(dac.duty_cycle * slope)
    time.sleep(0.1)

def midi_out():
    note = seq.advance()
    if note == 0:
        # maybe send AllNoteOff?
        pass
    if note > 20:
        midi.send(NoteOn(note, 120))

midi = adafruit_midi.MIDI(midi_in=usb_midi.ports[0], in_channel=1,
    midi_out=usb_midi.ports[1], out_channel=0)

def midi_in():
    k = midi.receive()
    if None != k:
        if isinstance(k, Start):
            seq.start()
            return
        if isinstance(k, Stop):
            seq.stop()
            return
        if hasattr(k, "control"):
            print(f"Ctrl:{k.control}={k.value} ch{k.channel}")
            if k.control==4:
                seq.playing = k.value==1
            if k.control==5:
                seq.set_tempo(k.value * 2)
            if k.control==6:
                seq.set_root(k.value)
        elif hasattr(k, "note"):
            print(f"NoteX:{k.note},{k.velocity} ch{k.channel}")
            seq.set_root(k.note)
        else:
            print(k)

if __name__ == "__main__":
    while True:
        if seq.playing:
            np[0]=(32,255,32)
        else:
            np[0]=(128,0,0)

        midi_in()
        midi_out()
