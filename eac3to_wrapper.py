# -*- coding: utf-8 -*-
import os
import re
import subprocess
from collections import OrderedDict


class Eac3toWrapper:
    def __init__(self):
        self.source_dir = ''
        self.eac3to_path = ''
        self.playlist_list = []

    def get_playlist(self):
        """
        Scan disc structure. Store brief playlist info in self.playlist_list[]
        :return:
        """
        if not os.path.isdir(self.source_dir):
            raise Exception('Invalid Blu-ray folder')
        parsed_source_dir = '"' + self.source_dir + '"'
        cli_template = [self.eac3to_path, parsed_source_dir]
        cli = ' '.join(cli_template)
        r = os.popen(cli)
        playlist_log = r.read()
        parsed_playlist_log = []
        for each in playlist_log.splitlines():
            parsed_playlist_log.append(str(each.replace("\x08", '').replace(' ''', '')))
        parsed_playlist_log.append('')

        playlist_flag = False
        m2ts_flag = False
        for line in parsed_playlist_log:
            if playlist_flag:
                if not m2ts_flag:
                    for each_m2ts in line.strip('[').strip('].m2ts').split('+'):
                        playlist_info['m2ts_list'].append(each_m2ts.zfill(5))
                    m2ts_flag = True
                    continue

            play_list_match = re.match(r'^\d+(?=\))', line)

            if line == '':
                self.playlist_list.append(playlist_info)
                playlist_flag = False
                m2ts_flag = False
                continue

            if play_list_match is not None:
                playlist_flag = True
                playlist_info = {
                    'playlist_num': play_list_match.group(),
                    'playlist': re.search(r'\d+(?=(.mpls))', line).group(),
                    'duration': '',
                    'm2ts_list': [],
                    'chapters': -1,
                    'tracks': []
                }

                if 'm2ts' in line:
                    m2ts_flag = True
                    playlist_info['m2ts_list'].append(re.search(r'\d+(?=(.m2ts))', line).group())
                    playlist_info['duration'] = re.search(r'(?<=.m2ts,)[0-9:]+', line).group()
                else:
                    playlist_info['duration'] = re.search(r'(?<=.mpls,)[0-9:]+', line).group()

    def playlist_scan(self, playlist_num):
        """
        Scan specific playlist
        Writing full eac3to analysis log to self.playlist_list
        :param playlist_num:
        :return:
        """
        playlist_info = self.playlist_list[playlist_num - 1]
        parsed_source_dir = '"' + self.source_dir + '"'
        cli_template = [self.eac3to_path, parsed_source_dir, playlist_info['playlist_num'] + ')']
        cli = ' '.join(cli_template)
        r = os.popen(cli)
        playlist_log = r.read()
        parsed_playlist_log = []
        for each in playlist_log.splitlines():
            parsed_playlist_log.append(str(each.replace("\x08", '').replace(' ''', '')))
        for line in parsed_playlist_log[1:]:
            if 'Chapters' in line:
                playlist_info['chapters'] = int(re.search(r'(?<=Chapters,)\d+', line).group())
                continue
            if not line.startswith('('):
                playlist_info['tracks'].append(line)
        self.playlist_list[playlist_num - 1] = playlist_info

    def chapter_scan(self, playlist_num):
        playlist_info = self.playlist_list[playlist_num - 1]
        parsed_source_dir = '"' + self.source_dir + '"'
        if playlist_info['chapters'] == -1:
            raise Exception('No Chapter Founded.')
        chapter_file_name = str(playlist_info['playlist']) + '_chapter.txt'
        cli_template = [self.eac3to_path, parsed_source_dir, playlist_info['playlist_num'] + ')',
                        '1:' + chapter_file_name, '-log=nul']
        cli = ' '.join(cli_template)
        subprocess.run(cli)
        chapter_info = OrderedDict({})
        with open(chapter_file_name, 'r') as f:
            for line in f.readlines():
                if 'NAME' not in line:
                    chapter_num = line[7:9]
                    chapter_time = line[-12:].strip('\n')
                    chapter_info[int(chapter_num)] = chapter_time

        os.remove(chapter_file_name)
        self.playlist_list[playlist_num - 1]['chapter_detail'] = chapter_info


if __name__ == '__main__':
    eac3to_test = Eac3toWrapper()
    eac3to_test.source_dir = r'G:\BluRay\Black.Hawk.Down.2001.COMPLETE.UHD.BLURAY-TERMiNAL'
    eac3to_test.eac3to_path = r'D:\Xin1Generator_v0.11\eac3to.exe'
    eac3to_test.get_playlist()
    eac3to_test.playlist_scan(1)
    eac3to_test.chapter_scan(1)
    print('ok')
