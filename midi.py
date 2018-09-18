Simple tool to extract a melody from .mid file suitable
to played back using pwm on a raspberry pi

Tip: use 
timidity <midi-file> 
for playback

Dependencies: 
mido
"""

import mido
import sys
import logging


def NoteToFreq(note):
    return 27.5 * 2.0 ** ((note - 21)/12)


def ExtractTrack(track):
    out = []
    t = 0
    active = {}
    secondary = {}
    for m in track:
        t += m.time
        # print (m)
        if m.type == "note_on":
            key = (m.channel, m.note)
            if len(active) > 0:
                secondary[key] = t
            active[key] = t
        elif m.type == "note_off":
            if len(active) > 1:
                logging.warning("multiple voices: %s", active)
            key = (m.channel, m.note)
            assert key in active
            if key in secondary:
                del secondary[key]
            else:
                out.append((m.note, t - active[key]))
            del active[key]
    return out


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    mid = mido.MidiFile(sys.argv[1])
    print ("TRACKS", mid.tracks)
    notes = ExtractTrack(mid.tracks[1])
    for note, dur in notes:
        print ("(%.3f, %d)," % (NoteToFreq(note), dur))

# for track in mid.tracks:
#    print ("=" * 60)
#    print (track)
#    print ("=" * 60)
#    ExtractTrack(track)
