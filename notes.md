Notes on File Format
--------------------

With only one exception, all files in the first directory have

	data[-165:-157] == data[-8:]

In all those cases:

	data[-12:-8] == [0, 0, 0, 157]

`157` being the negative offset of the trailer.

`data[-157:-12]` is of the form:

	000B VERNR:2.00; 0013 CEUSTYPE:K290S0108; 000F CEUSRELNR:2.03; 0013 COMBORELNR:2.06.01; 001B RECORDDATE:2012-01-10 1635; 0018 TITLE:REC092 01-101635;

The first four bytes appear to be a hex representation of the length of the part after the space.

The `TITLE` value matches the actual value in the filename in all but a couple of cases.

The raw data in the file is in `data[:-165]`. It is possible to have a file with no actual "data" in which case the length of the file is 165.

The raw data seems to consist of segments starting with `FF`.

These segments vary in length (including the `FF`) from 6 to 22+.

The first 3 bytes after the `FF` are monotonically increasing which suggests they may be timestamps. Note that they appear to monotonically increase across files.

The LSB of the timestamp seems to increment by 2 in most cases although jumps more occasionally. This suggests the timestamps are some sort of polling at regular intervals rather than only when some event happens. (Perhaps it's measuring the pressure on the keys at each point, not storing a value if no keys are pressed on that poll).

Note that an `FF` can appear in the timestamp so segments can't just be split on `FF`. On each `FF`, you read the next three bytes to get the time stamp and then read until the next `FF` to get the data for that timestamp.

If you look at the rest of the segment after the timestamp you get stuff like:

	6550 [46, 177, 53, 172, 58, 159, 62, 160, 65, 150, 70, 190]
	6552 [46, 177, 53, 167, 58, 155, 62, 156, 65, 144, 70, 188]
	6554 [46, 174, 53, 163, 58, 151, 62, 152, 65, 139, 70, 187]
	6556 [46, 171, 53, 158, 58, 146, 62, 147, 65, 132, 70, 186]
	6558 [46, 168, 53, 152, 58, 141, 62, 141, 65, 124, 70, 184]
	6560 [46, 164, 53, 146, 58, 136, 62, 135, 65, 116, 70, 182]
	6562 [46, 159, 53, 139, 58, 130, 62, 128, 65, 107, 70, 180]

Notice that it seems to be a list of pairs with the first of the pair constant and the second of the pair varying (and in this case, fading). One can easily imagine the first is what key is being pressed and the second is how hard it is being pressed.

That would mean that the keys `46`, `53`, `58`, `62`, `65` and `70` are being pressed at once.

Given there doesn't seem to be any separate mechanism for the pedals, it's likely that the numbers aren't just referring to keys but sensors in general and that this would include keys and pedals.

If we look at what values this first number in the pair takes in the first file we get

	36, 40, 42, 43, 46, 48, 50, 52, 54, 55, 56, 59, 60, 61, 62, 64, 65, 66, 67, 69 and 71

appearing over 30 times each with the most common being (in order) `55`, `50`, `59`, `43`, `62`, `67`, `71`, `57`, `69` and `64` (all appearing more than 1,000 times).

There are also between 1 and 4 occurrences of `164`, `168`, `170`, `171`, `176`, `178`, `180`, `182`, `183`, `185`, `187`, `188`, `190`, `192`, `195`, `197` and `199` so these must be other sensors, although given how many there are, they can't just be pedals.

The next question is, how do we map the common sensors to notes? If you assume they are the same as MIDI, the most common notes in the first file would be:

	G D B G D G B A A E

which looks pretty plausible for a piece in G major.

`46`, `53`, `58`, `62`, `65`, `70` would be

	Bb, F, Bb, D, F, Bb

so that file is ending on a Bb major chord. Interestingly, we can already tell from the file that the outer Bbs are released last.

Looking at the pressure contours, it appears that file `001` was a test.

`002` is much longer and the most common sensors polled are those for:

	G4 G5 A4 E4 D4 A5 B4 D6 D5 C4 F#5 E6 F#4 C6 B3 B5

along with sensor `111` (with over one million occurences!)

Presumably sensor `111` is the sustain pedal.

I still haven't quite yet calibrated the resolution of the timestamp but it seems plausible the timestamps are in milliseconds.

