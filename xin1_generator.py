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
    # source.playlist_scan(1)
    source.playlist_scan(2)
    # source.chapter_scan(1)
    source.chapter_scan(2)

    global_m2ts_frame_cache = {}
    for each in source.playlist_list:
        playlist_index = source.playlist_list.index(each)

        if each['tracks'] == []:
            continue

        source.playlist_list[playlist_index]['m2ts_info'] = {'00337': 15917, '00338': 3484, '00339': 2881, '00340': 616,
                                                             '00341': 11582, '00342': 1241, '00343': 863, '00344': 3951,
                                                             '00345': 4323, '00346': 1096, '00347': 9452, '00348': 598,
                                                             '00349': 2772, '00350': 2612, '00351': 25174, '00352': 778,
                                                             '00353': 18881, '00354': 582, '00355': 7037, '00356': 797,
                                                             '00357': 2457, '00358': 1446, '00359': 5744, '00360': 3802,
                                                             '00361': 3367, '00362': 1082, '00363': 5474, '00364': 822,
                                                             '00365': 33315, '00366': 649, '00367': 4971, '00368': 2470,
                                                             '00369': 5269, '00370': 4305, '00371': 2218, '00372': 4034,
                                                             '00373': 11538}
        # source.playlist_list[playlist_index]['frame_info'] = [0, 15917, 3484, 2881, 616, 11582, 1241, 863, 3951, 4323,
        #                                                       1096, 9452, 598, 2772, 2612, 25174, 778, 18881, 582, 7037,
        #                                                       797, 2457, 1446, 5744, 3802, 3367, 1082, 5474, 822, 33315,
        #                                                       649, 4971, 2470, 5269, 4305, 2218, 4034, 11538]

        source.playlist_list[playlist_index]['frame_info'] = [0, 15917, 19401, 22282, 22898, 34480, 35721, 36584,
                                                              40535, 44858, 45954, 55406, 56004, 58776, 61388, 86562,
                                                              87340, 106221, 106803, 113840, 114637, 117094, 118540,
                                                              124284, 128086, 131453, 132535, 138009, 138831, 172146,
                                                              172795, 177766, 180236, 185505, 189810, 192028, 196062,
                                                              207600]
        continue
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

    for each in source.playlist_list:
        virtual_offset = float(0)
        hide_next = False

        if each['tracks'] == []:
            continue

        for each_m2ts in each['m2ts_list']:
            idx = each['m2ts_list'].index(each_m2ts)
            start = float(each['frame_info'][idx]) / 23.97
            end = float(each['frame_info'][idx + 1]) / 23.976
            next_start = start

            for _, chapter_time in each['chapter_detail'].items():
                virtual_start = time2second(chapter_time)
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
