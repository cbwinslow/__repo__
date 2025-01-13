# File: generate_drum_groove.py
# Author: Blaine Winslow
# Date: 2025-01-12
# Purpose: Generates a MIDI drum groove for use in DAWs like Hydrogen or Waveform.
# Inputs: None
# Outputs: A MIDI file with a basic drum groove.

from mido import Message, MidiFile, MidiTrack

def create_drum_groove(file_name="drum_groove.mid"):
    """
    Generates a MIDI drum groove and saves it to a file.
    Instruments:
    - Kick: Note 36 (C1)
    - Snare: Note 38 (D1)
    - Hi-Hat Closed: Note 42 (F#1)
    """
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    # Time signature: 4/4
    tempo = 500000  # Microseconds per beat (120 BPM)

    # Add tempo meta message
    track.append(Message('program_change', program=0, time=0))

    # Drum pattern: 1 measure of 4/4
    # Kick on 1 and 3, Snare on 2 and 4, Hi-Hat on every 8th note
    pattern = [
        (36, 0),   # Kick
        (42, 120), # Hi-Hat
        (38, 120), # Snare
        (42, 120), # Hi-Hat
        (36, 120), # Kick
        (42, 120), # Hi-Hat
        (38, 120), # Snare
        (42, 120)  # Hi-Hat
    ]

    # Repeat the pattern for 4 measures
    for _ in range(4):
        for note, duration in pattern:
            track.append(Message('note_on', note=note, velocity=64, time=0))
            track.append(Message('note_off', note=note, velocity=64, time=duration))
    
    # Save the file
    mid.save(file_name)
    print(f"MIDI drum groove saved as {file_name}")

if __name__ == "__main__":
    create_drum_groove()
