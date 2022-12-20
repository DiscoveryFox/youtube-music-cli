import threading
import warnings
import urllib.parse
import os
import sys

import yt_dlp
import validators

import database
import yt_music_api
from models.Song import Song
from models.Playlist import Playlist

yt_dlp.extractor.common.InfoExtractor.report_warning = lambda *args, **kwargs: ...
yt_dlp.extractor.common.InfoExtractor.report_download_webpage = lambda *args, **kwargs: ...

warnings.filterwarnings("ignore")


def get_id(link: str) -> str:
    parsed_link = urllib.parse.urlparse(link)
    query = urllib.parse.parse_qs(parsed_link.query)
    return query.get('list')[0] if query.get('v') is None else query.get('v')[0]


class YoutubeDownloader:
    def __init__(self, output_directory: str, database_path: str):
        self.filepath: str = output_directory + '%(title)s.%(ext)s'
        self.output_directory = output_directory  # E.G.: r'C\User\Username\Desktop\Download\\'
        self.db: database.Database = database.Database(database_path)
        self.database_path = database_path
        self.api: yt_music_api.Api = yt_music_api.Api()

    def _download_song(self, link: str) -> int:
        if self.db.in_database(get_id(link)):
            return 0
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '96',
            }],
            'quiet': True,
            'outtmpl': self.filepath,
            "external_downloader_args": ['-loglevel', 'panic']
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=False)

            filename = f'{info["fulltitle"]} [{info["display_id"]}].wav'

            if info.get('uploader') is not None:
                channel = info.get('uploader')
            elif info.get('channel') is not None:
                channel = info.get('channel')
            else:
                channel = 'NOT DEFINED'

            title = info.get('title')

            print(f'Starting Download for '
                  f'{Song(name=title, id=get_id(link), creator=channel, filepath=self.output_directory + filename)}')

            self.db.register_song(Song(name=title,
                                       id=get_id(link),
                                       creator=channel,
                                       filepath=self.output_directory + filename)
                                  )

            ydl.download([link])

            self.db.confirm_song(get_id(link))
            return 1

    def _download_playlist(self, link: str):
        if self.db.in_database(get_id(link)):
            return 0

        threads: list[threading.Thread] = []

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '96',
            }],
            'quiet': True,
            'extract_flat': True,
            'outtmpl': self.filepath
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=False)

            if info.get('uploader') is not None:
                channel = info.get('uploader')
            elif info.get('channel') is not None:
                channel = info.get('channel')
            else:
                channel = 'NOT DEFINED'

            title = info.get('title')

            songs = list([url.get('url') for url in info.get('entries')])  # This should be a

            self.db.register_playlist(Playlist(name=title,
                                               id=get_id(link),
                                               creator=channel,
                                               songs=songs
                                               )
                                      )
            # loop through all songs in the playlist and start a download in a new thread for
            # every song
            for song in songs:
                song_thread = threading.Thread(target=self._download_song, name=get_id(song),
                                               args=(song,))
                threads.append(song_thread)
            [thread.start() for thread in threads]  # Start all threads
            [thread.join() for thread in threads]  # Wait for all threads to finish

            self.db.confirm_playlist(get_id(link))

    def download(self, link: str):
        if not validators.url(link):
            return 'link not valid'
        parsed_link = urllib.parse.urlparse(link)
        query = urllib.parse.parse_qs(parsed_link.query)
        link_type: str = 'playlist' if query.get('v') is None else 'song'
        if link_type == 'playlist':
            self._download_playlist(link)
        else:
            self._download_song(link)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
