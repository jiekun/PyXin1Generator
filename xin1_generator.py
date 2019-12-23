# -*- coding: utf-8 -*-

import os

from collections import OrderedDict

from eac3to_wrapper import Eac3toWrapper
from ffmpeg_wrapper import get_video_frame_count


def time2second(t):
    h, m, s = t.strip().split(":")
    return int(h) * 3600 + int(m) * 60 + float(s)


def floatsec2time(f):
    m, s = divmod(f, 60)
    h, m = divmod(m, 60)
    s, ms = str(s).split('.')

    h = str(int(h)).zfill(2)
    m = str(int(m)).zfill(2)
    s = str(s).zfill(2)
    ms = str(ms)[0:3]
    return ':'.join([h, m, s]) + '.' + ms


def xin1_generator():
    source = Eac3toWrapper()
    source.source_dir = r'G:\BluRay\Black.Hawk.Down.2001.COMPLETE.UHD.BLURAY-TERMiNAL'
    source.eac3to_path = r'D:\Dev\AutoEncoding\tools\eac3to\eac3to.exe'
    source.get_playlist()
    source.playlist_scan(1)
    source.playlist_scan(2)
    source.chapter_scan(1)
    source.chapter_scan(2)

    global_m2ts_frame_cache = {}
    for each in [source.playlist_list[0], source.playlist_list[1]]:
        playlist_index = source.playlist_list.index(each)

        if each['tracks'] == []:
            continue

        source.playlist_list[playlist_index]['m2ts_info'] = {}
        source.playlist_list[playlist_index]['frame_info'] = []

        # continue
        each['m2ts_info'] = {}
        for each_m2ts in each['m2ts_list']:
            media_path = os.path.join(source.source_dir, 'BDMV', 'STREAM', each_m2ts + '.m2ts')
            if each_m2ts in global_m2ts_frame_cache:
                frame_count = global_m2ts_frame_cache[each_m2ts]
            else:
                frame_count = get_video_frame_count(media_path)
                global_m2ts_frame_cache[each_m2ts] = frame_count

            source.playlist_list[playlist_index]['m2ts_info'][each_m2ts] = frame_count
            source.playlist_list[playlist_index]['frame_info'].append(frame_count)

    merge_file_list = []
    merge_frame_list = [0]
    frame_sum = 0
    for each in [source.playlist_list[0], source.playlist_list[1]]:
        if each['tracks'] == []:
            continue
        for each_m2ts in each['m2ts_list']:
            idx = each['m2ts_list'].index(each_m2ts)
            if each_m2ts not in merge_file_list:
                merge_file_list.append(each_m2ts)
                m2ts_frame_count = each['frame_info'][idx]
                frame_sum += m2ts_frame_count
                merge_frame_list.append(frame_sum)

    for each in [source.playlist_list[1], source.playlist_list[0]]:
        print('\n------------------EditionBreak----------------------\n')
        virtual_offset = float(0)
        hide_next = False

        if each['tracks'] == []:
            continue

        for each_m2ts in each['m2ts_list']:
            idx = merge_file_list.index(each_m2ts)
            start = float(merge_frame_list[idx]) / 23.976
            end = float(merge_frame_list[idx + 1]) / 23.976
            next_start = start

            for _, chapter_time in each['chapter_detail'].items():
                tmp_virtual_start = time2second(chapter_time)
                # virtual_start = (tmp_virtual_start * 23.976) / 23.9726
                virtual_start = tmp_virtual_start
                if virtual_offset < virtual_start <= virtual_offset + end - start:
                    print(floatsec2time(next_start), floatsec2time(start + virtual_start - virtual_offset), hide_next)
                    next_start = start + virtual_start - virtual_offset
                    hide_next = False

            virtual_offset += end - start
            if next_start == end:
                continue

            print(floatsec2time(next_start), floatsec2time(end), hide_next)
            hide_next = True


if __name__ == '__main__':
    xin1_generator()
