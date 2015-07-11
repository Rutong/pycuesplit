#!/usr/bin/env python

from subprocess import call
import os.path
import argparse
import re

parser = argparse.ArgumentParser(description='encode FLAC using FFMPEG from CUE file')
parser.add_argument('-i','--input', metavar='<cue file>', help='CUE file',required=True)
parser.add_argument('-t','--track', metavar='<track number>', help='Extract one track', default=0, type=int, required=False)
parser.add_argument('-f','--format', metavar='<output format>', help='Output format, choose from flac, mp3, aac', choices=['flac', 'mp3', 'aac'], default='flac', required=False)
parser.add_argument('-a','--albumart', metavar='<image file>', help='PNG or JPG to be added as albumart (only work for mp3)', required=False)
parser.add_argument('-y','--overwrite', action='store_true', help='Overwrite output files without asking.', required=False)
parser.add_argument('-d','--dry-run',action='store_true',help='Skip encoding, print ffmpeg command line and exit', required=False)

args = parser.parse_args()

cue_file=None
albumart_file=None

if os.path.isfile(args.input):
    cue_file=args.input
else:
    print 'CUE file not found'
    exit()

if args.albumart!=None:
    if os.path.isfile(args.albumart):
        albumart_file=args.albumart
    else:
        print 'albumart file not found'
        exit()

cue_data = open(cue_file).read().splitlines()

disk_metadata = {}
tracks = []
media_file = None


for line in cue_data:
    if line.startswith('FILE '):
        media_file = re.findall('"([^"]*)"', line)

if len(media_file) != 1 or not os.path.isfile(media_file[0]):
    print 'media file not found'
    exit()

media_file=media_file[0]

print "processing %s,%s...\n"%(cue_file,media_file)

for line in cue_data:
    if line.startswith('PERFORMER '):
        disk_metadata['artist'] = re.findall('"([^"]*)"', line)[0]
    if line.startswith('TITLE '):
        disk_metadata['album'] = re.findall('"([^"]*)"', line)[0]
    if line.startswith('REM GENRE '):
        disk_metadata['genre'] = ' '.join(line.split(' ')[2:])
    if line.startswith('REM DATE '):
        disk_metadata['date'] = ' '.join(line.split(' ')[2:])

    if line.startswith('  TRACK '):
        track = disk_metadata.copy()
        track['track'] = int(re.findall('[0-9][0-9]', line)[0], 10)
        tracks.append(track)

    if line.startswith('    TITLE '):
        tracks[-1]['title'] = re.findall('"([^"]*)"', line)[0]
    if line.startswith('    PERFORMER '):
        tracks[-1]['artist'] = re.findall('"([^"]*)"', line)[0]
    if line.startswith('    INDEX 01 '):
        t = map(int, re.findall('[0-9][0-9]', line))
        tracks[-1]['start'] = 60000 * t[1] + 1000 * t[2] + 10 * t[3]

for i in range(len(tracks)):
    if i != len(tracks) - 1:
        tracks[i]['duration'] = tracks[i + 1]['start'] - tracks[i]['start']

for track in tracks:
    pcmd = ['ffmpeg']
    metadata = {
        'artist': track['artist'],
        'title': track['title'],
        'album': track['album'],
        'track': str(track['track']) + '/' + str(len(tracks))
    }

    if 'genre' in track:
        metadata['genre'] = track['genre']
    if 'date' in track:
        metadata['date'] = track['date']

    pcmd = ['ffmpeg']

    if args.overwrite:
        pcmd.append("-y")

    pcmd.append("-i")
    pcmd.append(media_file)
    pcmd.append("-ss")
    pcmd.append('%.2d:%.2d:%.2d.%.3d' % (track['start'] / 60 / 60 / 1000, track['start'] / 60 / 1000 % 60, track['start'] / 1000 % 60, track['start'] % 1000))

    if 'duration' in track:
        pcmd.append("-t")
        pcmd.append('%.2d:%.2d:%.2d.%.3d' % (track['duration'] / 60 / 60 / 1000, track['duration'] / 60 / 1000 % 60, track['duration'] / 1000 % 60, track['duration'] % 1000))


    pcmd.append('-id3v2_version')
    pcmd.append('3')

    for (k, v) in metadata.items():
        pcmd.append('-metadata')
        pcmd.append('%s=%s' % (k, v))

    output_file = None;
    if args.format=='flac':
        output_file='%.2d.flac' % track['track']
    elif args.format=='mp3':
        pcmd.append('-ab')
        pcmd.append('320000')        
        output_file='__TEMP__%.2d.mp3' % track['track']
    elif args.format=='aac':
        pcmd.append('-acodec')
        pcmd.append('libfdk_aac')
        pcmd.append('-ab')
        pcmd.append('320000')        
        output_file='%.2d.mp4' % track['track']

    pcmd.append(output_file)

    if track['track'] == args.track or args.track == 0:
        print ' '.join(pcmd)
        if not args.dry_run:
            call(pcmd)
        
        if albumart_file != None and args.format=='mp3':
            pcmd = ['ffmpeg'];
            pcmd.append("-y")
            pcmd.append("-i")
            pcmd.append(output_file)
            pcmd.append("-i")
            pcmd.append(albumart_file)
            pcmd.append("-map")
            pcmd.append('0:0')
            pcmd.append("-map")
            pcmd.append('1:0')
            pcmd.append("-c")
            pcmd.append('copy')
            pcmd.append('-id3v2_version')
            pcmd.append('3')
            pcmd.append("-metadata:s:v")
            pcmd.append('title=Album cover')
            pcmd.append("-metadata:s:v")
            pcmd.append('comment=Cover (Front)')
            pcmd.append(output_file[8:]) 
            print ' '.join(pcmd)
            if not args.dry_run:
                call(pcmd)


