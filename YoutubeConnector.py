import asyncio
import platform
import queue
import sqlite3
from pprint import pprint
import selenium.common.exceptions
import time
import os
import threading
import wave
# portaudio19
from queue import Queue
from typing import List, Tuple
import json
import pyaudio
import playsound
import requests
import selenium.webdriver
import selenium.webdriver.remote.webelement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import requests
import selenium
import undetected_chromedriver as uc
from urllib.parse import quote
from multiprocessing import Process

from pydub import AudioSegment
import pydub.playback

import kthread
import sys
import yt_dlp

import yt_dlp.extractor.common

yt_dlp.extractor.common.InfoExtractor.report_warning = lambda *args, **kwargs: ...
yt_dlp.extractor.common.InfoExtractor.report_download_webpage = lambda *args, **kwargs: ...


def remove_playlist_link_part(songlist: list[str]):
    return [(song[0].split('&')[0], song[1], song[2]) for song in songlist]


class Playlist:
    def __init__(self, name: str, creator: str, SongQueue):
        self.queue = SongQueue
        self.name = name
        self.creator = creator


class Song:
    def __init__(self, name: str, filepath, creator):
        self.name = name
        self.filepath = filepath
        self.creator = creator


class AudioHandler:
    def __init__(self, path: str):
        self.path = path
        self.audio = AudioSegment.from_wav(path)
        print(path)
        self.main_thread = kthread.KThread(target=pydub.playback.play, args=(self.audio,),
                                           name='MusicThread')

    def _callback(self, in_data, frame_count, time_info, status):
        # Deprecated
        data = self.wf.readframes(frame_count)
        print(time_info, status, in_data)
        return data, pyaudio.paContinue

    def change_volume(self):
        self.audio

    def _start(self):
        self.wf = wave.open(self.path, 'rb')
        self.stream = self.audio.open(format=self.audio.get_format_from_width(
            self.wf.getsampwidth()),
            channels=self.wf.getnchannels(),
            rate=self.wf.getframerate(),
            output=True,
            stream_callback=self.callback
        )
        self.stream.start_stream()
        try:
            while self.stream.is_active():
                time.sleep(0.1)
        except OSError:
            pass

    def start(self):

        self.main_thread.start()

    def stop(self):
        self.main_thread.terminate()

    def _stop(self):
        self.stream.stop_stream()
        self.stream.close()
        self.wf.close()
        self.audio.terminate()
        try:
            self.audio.close(self.stream)
        except ValueError:
            pass

# TODO: Check if the return values of .fetchone() and .fetchall() are valid.
class Database:
    def __init__(self, path: str):
        self.connection = sqlite3.Connection(path)
        self.cursor = self.connection.cursor()
        self.create()

    def create(self):
        self.cursor.execute('CREATE TABLE IF NOT EXISTS songs ('
                            'name TEXT PRIMARY KEY NOT NULL, '
                            'filepath TEXT UNIQUE NOT NULL,'
                            'creator TEXT NOT NULL'
                            ')')

        self.cursor.execute('CREATE TABLE IF NOT EXISTS playlists('
                            'name TEXT PRIMARY KEY NOT NULL,'
                            'songs BLOB NOT NULL'
                            ')')
        self.connection.commit()

    def save_song(self, name: str, filename: str, creator: str):
        __new_cursor = self.connection.cursor()
        __new_cursor.execute('''INSERT INTO songs VALUES (?, ?, ?)''', (name, filename, creator))
        self.connection.commit()

    def load_all_songs(self):
        __new_cursor = self.connection.cursor()
        __new_cursor.execute('SELECT * FROM songs')
        songs = __new_cursor.fetchall()
        return songs

    def load_song(self, name: str):
        __new_cursor = self.connection.cursor()
        __new_cursor.execute('SELECT * FROM songs WHERE name = ?', name)
        song = __new_cursor.fetchone()
        return Song(song[0], song[1], song[2])

    def load_playlist(self, name: str):
        __new_cursor = self.connection.cursor()
        __new_cursor.execute('SELECT * FROM playlists WHERE name = ?', name)
        result = __new_cursor.fetchall()
        simple_queue = queue.Queue()
        [simple_queue.put(song) for song in json.loads(result[1])]
        return Playlist(result[0], simple_queue)


class YoutubeMusic:
    logged_in: bool

    def __init__(self, driver: selenium.webdriver.Chrome = None,
                 email: bool = None,
                 password: bool = None,
                 timeout: int = 15) -> None:
        """
    The Object to interact with the Website. Everything will be ran through that class.

    :param driver: A Selenium Webdriver Object
    :param email: The Google email to log into a Google account
    :param password: The password to log into the provided Google account
    :param timeout: The time the page can take to load. The Timeout before an exception is thrown.
        """
        self.musicthread = None
        self.db = Database('cache\\songs.db')
        if driver is None:
            self.chrome_options = selenium.webdriver.chrome.options.Options()
            self.chrome_options.add_argument('start-maximized')
            self.chrome_options.add_argument('--lang=en_US')
            self.chrome_options.add_argument('--headless')
            self.chrome_options.add_argument(
                '--user-agent = Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1')

            self.driver = uc.Chrome(options=self.chrome_options)
        else:
            self.driver = driver

        self.musicplayer = None
        self.audioplayer = None
        self.logged_in = False
        self.email = email
        self.password = password
        self.timeout = timeout
        self.queue: Queue = Queue()

        self.setup()

        if self.email is not None and self.password is not None:
            self.logged_in = self.login(email, password)
            if not self.logged_in:
                raise Exception('You provided the wrong email/password')

    def login(self,
              email: str,
              password: str) -> bool:
        # Maybe add later. For now there is no Login
        #  with selenium
        self.driver.find_element(By.XPATH, '//*[@id="right-content"]/a').click()
        WebDriverWait(driver=self.driver, timeout=self.timeout).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="identifierId"]')))

        self.driver.find_element(By.XPATH, '//*[@id="identifierId"]').send_keys(self.email)
        self.driver.find_element(By.XPATH, '//*[@id="identifierNext"]/div/button').click()

    def setup(self):
        self.driver.get('https://music.youtube.com')

        WebDriverWait(self.driver, timeout=self.timeout).until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div[1]/div/div/div[2]/div[1]/div['
                       '3]/div[1]/form[2]/div/div/button')))

        self.driver.find_element(By.XPATH,
                                 '//*[@id="yDmH0d"]/c-wiz/div[1]/div/div/div[2]/div[1]/div['
                                 '3]/div[1]/form[2]/div/div/button').click()

    def search_song(self, keywords: str, length: int = 5) -> list[tuple[str, str, str]]:
        result: list[tuple[str, str, str]] = []

        self.driver.get(f'https://music.youtube.com/search?q={quote(keywords)}')

        WebDriverWait(self.driver, timeout=self.timeout).until(EC.presence_of_element_located((
            By.XPATH, '//*[@id="contents"]/ytmusic-shelf-renderer[2]')))

        expand_button = self.driver.find_element(By.XPATH,
                                                 '//*[@id="contents"]/ytmusic-shelf-renderer[2]/div[6]/a/tp-yt-paper-button')
        WebDriverWait(self.driver, timeout=self.timeout).until(EC.element_to_be_clickable((
            By.XPATH, '//*[@id="contents"]/ytmusic-shelf-renderer[2]/div[6]/a/tp-yt-paper-button')))
        expand_button.click()

        time.sleep(3)

        song_container = self.driver.find_element(By.XPATH,
                                                  '/html/body/ytmusic-app/ytmusic-app-layout/'
                                                  'div[3]/ytmusic-search-page/ytmusic-tabbed-search-results-renderer/div[2]/ytmusic-section-list-renderer/div[2]/ytmusic-shelf-renderer/div[3]')

        songs_tags: list[selenium.webdriver.remote.webelement.WebElement] = \
            song_container.find_elements(By.XPATH, './*')
        songs_tags = songs_tags[0:length]
        for song in songs_tags:
            link_tag = song.find_element(By.TAG_NAME, 'a')
            link = link_tag.get_attribute('href')
            with yt_dlp.YoutubeDL(
                    {'quiet': True, "external_downloader_args": ['-loglevel', 'panic']}) as ydl:
                ydl: yt_dlp.YoutubeDL
                info = ydl.extract_info(link,
                                        download=False)
                result.append((link, info['title'], info['channel']))

        return result

    def search_official_playlists(self, keywords: str, length: int = 5) -> list[tuple[str, str,
    str]]:
        result: list[tuple[str, str, str]] = []

        self.driver.get(f'https://music.youtube.com/search?q={quote(keywords)}')

        WebDriverWait(self.driver, timeout=self.timeout).until(EC.presence_of_element_located((
            By.XPATH, '//*[@id="contents"]/ytmusic-shelf-renderer[5]')))

        expand_button = self.driver.find_element(By.XPATH,
                                                 '//*[@id="contents"]/ytmusic-shelf-renderer[5]/div[6]/a/tp-yt-paper-button')
        try:
            WebDriverWait(self.driver, timeout=self.timeout).until(EC.element_to_be_clickable(
                (By.XPATH,
                 '//*[@id="contents"]/ytmusic-shelf-renderer[5]/div[6]/a/tp-yt-paper-button')
            ))
        except selenium.common.exceptions.TimeoutException:
            new_options = selenium.webdriver.chrome.options.Options()
            new_options.add_argument('start-maximized')
            new_options.add_argument('--lang=en_US')
            new_options.add_argument('--headless')
            new_options.add_argument(
                '--user-agent = Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1')

            self.driver = uc.Chrome(options=new_options)

        expand_button.click()

        time.sleep(3)

        playlist_container = self.driver.find_element(By.XPATH,
                                                      '/html/body/ytmusic-app/ytmusic-app-layout/'
                                                      'div[3]/ytmusic-search-page/ytmusic-tabbed-'
                                                      'search-results-renderer/div[2]/ytmusic-'
                                                      'section-list-renderer/div[2]/ytmusic-shelf'
                                                      '-renderer/div[3]')
        playlist_tags = playlist_container.find_elements(By.XPATH, './*')

        playlist_tags = playlist_tags[0:length]

        for index, playlist in enumerate(playlist_tags):
            link_tag = playlist.find_element(By.TAG_NAME, 'a')
            link = link_tag.get_attribute('href')

            ydl_opts = {
                'extract_flat': True,
                'quiet': True,
                "external_downloader_args": ['-loglevel', 'panic']
            }

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl: yt_dlp.YoutubeDL
                info = ydl.extract_info(link,
                                        download=False)

                result.append((link, info['title'], info['uploader']))

        return result

    def _fetch_songs_from_playlist(self, url: str, length: str | int = 'full') -> list[tuple[str,
    str,
    str]]:
        result: list[tuple[str, str, str]] = []
        # new_driver = uc.Chrome(self.driver.)
        options = selenium.webdriver.chrome.options.Options()
        options.add_argument('--headless')
        new_driver: selenium.webdriver.Chrome = uc.Chrome(options=options)
        print('Starting new Driver')
        new_driver.get(url[0])

        WebDriverWait(new_driver, timeout=self.timeout).until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div[1]/div/div/div[2]/div[1]/div['
                       '3]/div[1]/form[2]/div/div/button')))

        new_driver.find_element(By.XPATH,
                                '//*[@id="yDmH0d"]/c-wiz/div[1]/div/div/div[2]/div[1]/div['
                                '3]/div[1]/form[2]/div/div/button').click()

        WebDriverWait(new_driver, self.timeout).until(EC.presence_of_element_located((By.XPATH,
                                                                                      '/html/body/ytmusic-app/ytmusic-app-'
                                                                                      'layout/div[3]/ytmusic-browse-response'
                                                                                      '/div[2]/ytmusic-section-list-renderer'
                                                                                      '/div[2]/ytmusic-playlist-shelf-'
                                                                                      'renderer/div[1]')))

        song_container = new_driver.find_element(By.XPATH, '/html/body/ytmusic-app/ytmusic-app-'
                                                           'layout/div[3]/ytmusic-browse-response'
                                                           '/div[2]/ytmusic-section-list-renderer'
                                                           '/div[2]/ytmusic-playlist-shelf-'
                                                           'renderer/div[1]')
        song_tags = song_container.find_elements(By.XPATH, './*')
        if length != 'full':
            song_tags = song_tags[0:length]
        for index, song in enumerate(song_tags):
            print(song)

            link_tag = song.find_element(By.TAG_NAME, 'a')
            link = link_tag.get_attribute('href')

            with yt_dlp.YoutubeDL({'quiet': True,
                                   "external_downloader_args": ['-loglevel', 'panic'],
                                   'extract_flat': True}) as ydl:
                ydl: yt_dlp.YoutubeDL
                info = ydl.extract_info(link,
                                        download=False)
            try:
                result.append((link, info['title'], info['uploader']))
            except KeyError:
                try:
                    result.append((link, info['title'], info['channel']))
                except KeyError:
                    result.append((link, info['title'], 'Youtube'))
        new_driver.close()
        return result

    def add_song(self, url: tuple[str, str, str]):
        self.queue.put(self.download(url))

    def add_song_to_queue(self, SongName: str):
        self.queue.put({'type': 'song', 'name': SongName})

    def add_playlist(self, url: tuple[str, str, str], force_order: bool = False, length: str | int =
    'full'):
        songlist = self._fetch_songs_from_playlist(url, length=length)
        songlist = remove_playlist_link_part(songlist)
        self.queue.put(self.download(songlist[0]))
        del songlist[0]
        if not force_order:
            threading.Thread(target=lambda: [self.queue.put(self.download(song)) for song in
                                             songlist]).start()
        else:
            [self.queue.put(self.download(song)) for song in songlist]

    def add_playlist_to_queue(self, PlaylistName):
        # self.queue.put({'type': 'playlist', 'name': PlaylistName})
        for song in self.db.load_playlist(PlaylistName).queue:
            self.queue.put({'type': 'song', 'name': song.name})


    def download(self, url: tuple[str, str, str]) -> tuple[str, str, str]:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '96',
            }],
            'quiet': True,
            "external_downloader_args": ['-loglevel', 'panic']
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url[0])
            if os.path.isdir('cache'):
                ...
            else:
                os.mkdir('cache')

            filename = f'{info["fulltitle"]} [{info["display_id"]}].wav'

            if info.get('uploader') is not None:
                channel = info.get('uploader')
            elif info.get('channel') is not None:
                channel = info.get('channel')
            else:
                channel = 'NOT DEFINED'

            self.db.save_song(info['title'], filename, channel)

            if platform.platform() == 'Windows':
                try:
                    os.rename(filename, f'cache/{filename}')
                except FileExistsError:
                    os.remove(filename)
                return (os.path.abspath(f'cache\\{filename}'),
                        url[1],
                        url[2])
            else:
                try:
                    os.rename(filename, f'cache/{filename}')
                except FileExistsError:
                    os.remove(filename)
                return (os.path.abspath(f'cache/{filename}'),
                        url[1],
                        url[2])

    def play(self, spam=True):
        if self.queue.unfinished_tasks == 0 and spam:
            print('No Songs currently in queue')
            time.sleep(0.5)
            self.play()

        path: dict = self.queue.get()

        if path.get('type') == 'song':
            song: Song = self.db.load_song(path.get('name'))

        print(f'Now plays {song.name} from {song.creator}')

        # self.audioplayer = pyaudio.PyAudio()
        self.musicplayer = AudioHandler(path[0])  # , self.audioplayer)
        # self.musicthread = threading.Thread(target=self.musicplayer.start)
        print('Starting Musicplayer')
        self.musicplayer.start()
        print('Musicplayer started')

    def stop(self):
        self.musicplayer.stop()

    def skip(self):
        self.stop()
        self.play()

    @staticmethod
    def cleanup():
        temp_dir = os.listdir()
        for file in temp_dir:
            if file.endswith('.wav') or file.endswith('.part'):
                try:
                    os.remove(os.path.abspath(file))
                except PermissionError:
                    pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()
