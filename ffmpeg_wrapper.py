# -*- coding: utf-8 -*-

import re
from subprocess import Popen, PIPE, STDOUT


def get_video_frame_count(file_path):
    parse_path = '"' + file_path + '"'
    cli = 'ffmpeg.exe -i %s -map 0:v:0 -c copy -f null -' % parse_path
    p = Popen(cli, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT)
    ffmpeg_scan = p.stdout.read()
    frame_count = re.findall(r'\d+(?= fps=)', ffmpeg_scan.decode('utf-8'))[-1]
    return int(frame_count)


if __name__ == '__main__':
    frame_count = get_video_frame_count(r'G:\BluRay\Black.Hawk.Down.2001.COMPLETE.UHD.BLURAY-TERMiNAL\BDMV\STREAM\00374'
                                   r'.m2ts')
    print(frame_count)
    frame_count = get_video_frame_count(r'G:\BluRay\Black.Hawk.Down.2001.COMPLETE.UHD.BLURAY-TERMiNAL\BDMV\STREAM\00359'
                                        r'.m2ts')
    print(frame_count)
    frame_count = get_video_frame_count(
        r'G:\BluRay\Black.Hawk.Down.2001.COMPLETE.UHD.BLURAY-TERMiNAL\BDMV\STREAM\00355'
                                   r'.m2ts')
    print(frame_count)
