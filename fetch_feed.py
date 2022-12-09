import time
import os
import threading
import wave
# portaudio19
from queue import Queue
import pyaudio
import playsound
import selenium.webdriver
import selenium.webdriver.remote.webelement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from urllib.parse import quote

import sys
import yt_dlp


class AudioHandler:
    def __init__(self, path: str, audio: pyaudio.PyAudio):
        self.stream = None
        self.audio = audio
        self.wf = None
        self.path = path

    def callback(self, in_data, frame_count, time_info, status):
        data = self.wf.readframes(frame_count)
        return data, pyaudio.paContinue

    def start(self):
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

    def stop(self):
        self.stream.stop_stream()
        self.stream.close()
        self.wf.close()
        self.audio.terminate()
        try:
            self.audio.close(self.stream)
        except ValueError:
            pass


class YoutubeMusic:
    logged_in: bool

    def __init__(self, driver: selenium.webdriver.Chrome,
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
        self.musicplayer = None
        self.audioplayer = None
        self.driver = driver
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

    def search(self, keywords: str) -> list[str]:
        result: list[str] = []
        print(f'Search Term: ', end='')
        print(f'https://music.youtube.com/search?q={quote(keywords)}')

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
                                                  'div[3]/ytmusic-search-page/ytmusic-tabbed-'
                                                  'search-results-renderer/div[2]/ytmusic-'
                                                  'section-list-renderer/div[2]/ytmusic-'
                                                  'shelf-renderer/div[3]')

        songs_tags: list[selenium.webdriver.remote.webelement.WebElement] = \
            song_container.find_elements(By.XPATH, './*')

        for song in songs_tags:
            link_tag = song.find_element(By.TAG_NAME, 'a')
            link = link_tag.get_attribute('href')
            result.append(link)

        return result

    def add_song(self, url: str):
        self.queue.put(self.download(url))

    def download(self, url: str) -> str:
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'wav',
                'preferredquality': '96',
            }]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl: yt_dlp.YoutubeDL
            info = ydl.extract_info(url)
            return os.path.abspath(f'{info["fulltitle"]} [{info["display_id"]}].wav')

    def play(self):
        path = self.queue.get()

        self.audioplayer = pyaudio.PyAudio()
        self.musicplayer = AudioHandler(path, self.audioplayer)
        musicthread = threading.Thread(target=self.musicplayer.start)
        musicthread.start()

    def stop(self):
        self.musicplayer.stop()

    def skip(self):
        self.stop()
        self.play()
