# pycuesplit
encode FLAC/MP4/AAC using FFMPEG from CUE file

```
usage: pycuesplit.py [-h] -i <cue file> [-t <track number>]
                     [-f <output format>] [-a <image file>] [-y] [-d]

arguments:
  -h, --help            show this help message and exit
  -i <cue file>, --input <cue file>
                        CUE file
  -t <track number>, --track <track number>
                        Extract one track
  -f <output format>, --format <output format>
                        Output format, choose from flac, mp3, aac
  -a <image file>, --albumart <image file>
                        PNG or JPG to be added as albumart (only works for mp3)
  -y, --overwrite       Overwrite output files without asking.
  -d, --dry-run         Skip encoding, print ffmpeg command line and exit
```