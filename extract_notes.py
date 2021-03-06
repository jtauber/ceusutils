#!/usr/bin/env python

import struct
import sys


def get(data, start, end=None):
    if end is None:
        return [ord(datum) for datum in data[start:]]
    else:
        return [ord(datum) for datum in data[start:end]]


def midi2note(midi):
    d, m = divmod(midi, 12)
    return ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"][m] + str(d)


FILENAME = sys.argv[1]
THRESHOLD = 10


with open(FILENAME) as f:
    data = f.read()

assert get(data, -165, -157) == get(data, -8)
assert get(data, -8, -3) == [0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
assert get(data, -12, -8) == [0, 0, 0, 157]

# load trailer

trailer = {}
offset = -157

while offset < -12:
    length = int(data[offset:offset + 4], 16)
    assert data[offset + 4] == " "
    trailer_entry = data[offset + 5: offset + 5 + length]
    offset += 5 + length
    assert trailer_entry[-1] == ";"
    key, value = trailer_entry[:-1].split(":")
    trailer[key] = value

segments = []
last_start = 0

for i in range(len(data) - 165):
    if ord(data[i]) == 0xFF:
        if last_start and i > last_start + 4:
            segment = data[last_start:i]
            segments.append(segment)
        last_start = i

segment = data[last_start:i]
segments.append(segment)

notes = []
start_time = {}
for segment in segments:
    assert len(segment) > 4
    timestamp = struct.unpack(">I", "\x00" + segment[1:4])[0]

    pressure = {}

    for i in range(4, len(segment), 2):
        if i + 1 < len(segment):
            x = ord(segment[i])
            y = ord(segment[i + 1])
            if y > THRESHOLD:
                pressure[x] = y

    prev = set(start_time.keys())
    started = set(pressure.keys()) - prev
    ended = prev - set(pressure.keys())
    for k in started:
        start_time[k] = timestamp
    for k in ended:
        if k <= 108:
            note = midi2note(k)
        else:
            note = "-"
        notes.append((start_time[k], k, note, timestamp))
        del start_time[k]

for start, key, note, end in sorted(notes):
    print start, key, note, end
