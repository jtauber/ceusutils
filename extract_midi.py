#!/usr/bin/env python

import struct
import sys

import midiwrite


def get(data, start, end=None):
    if end is None:
        return [ord(datum) for datum in data[start:]]
    else:
        return [ord(datum) for datum in data[start:end]]


FILENAME = sys.argv[1]
THRESHOLD = 48


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

notes1 = []
notes2 = []
notes3 = []
start_time = {}
peak_pressure = {}
peak_time = {}
for segment in segments:
    assert len(segment) > 4
    timestamp = struct.unpack(">I", "\x00" + segment[1:4])[0]

    if timestamp % 2 != 0:  # not sure why
        continue

    pressure = {}

    for i in range(4, len(segment), 2):
        if i + 1 < len(segment):
            x = ord(segment[i])
            y = ord(segment[i + 1])
            if y > THRESHOLD:
                pressure[x] = y
                if pressure[x] > peak_pressure.get(x, 0):
                    peak_pressure[x] = pressure[x]
                    peak_time[x] = timestamp

    prev = set(start_time.keys())
    started = set(pressure.keys()) - prev
    ended = prev - set(pressure.keys())
    for k in started:
        start_time[k] = timestamp
    for k in ended:
        if k <= 108:
            velocity = peak_time[k] - start_time[k]
            duration = max(0, timestamp - start_time[k])
            if peak_pressure[k] > 160:
                notes1.append((start_time[k], k, max(0, min(127, peak_pressure[k] / 2)), timestamp - start_time[k]))
            notes2.append((start_time[k], k, max(0, min(127, peak_pressure[k] / 2)), timestamp - start_time[k]))
            notes3.append((start_time[k], k, max(0, min(127, velocity)), timestamp - start_time[k]))
        del start_time[k]
        del peak_pressure[k]
        del peak_time[k]

s = midiwrite.SMF([notes1, notes2, notes3])

with open("test.mid", "w") as f:
    s.write(f)
