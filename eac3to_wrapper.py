# -*- coding: utf-8 -*-
import os
import io
import re


class Eac3toWrapper:
    def __init__(self):
        self.source_dir = ''
        self.eac3to_path = ''
        self.playlist_list = []

    def get_playlist(self):
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
                    'chapters': 0,
                    'tracks': []
                }

                if 'm2ts' in line:
                    m2ts_flag = True
                    playlist_info['m2ts_list'].append(re.search(r'\d+(?=(.m2ts))', line).group())
                    playlist_info['duration'] = re.search(r'(?<=.m2ts,)[0-9:]+', line).group()
                else:
                    playlist_info['duration'] = re.search(r'(?<=.mpls,)[0-9:]+', line).group()

    def playlist_scan(self, playlist_num):
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


if __name__ == '__main__':
    eac3to_test = Eac3toWrapper()
    eac3to_test.source_dir = r'V:\\'
    eac3to_test.eac3to_path = r'D:\Xin1Generator_v0.11\eac3to.exe'
    eac3to_test.get_playlist()
    eac3to_test.playlist_scan(1)
    print('ok')
