import time
import selenium
from selenium.webdriver.chrome.service import Service
from selenium.webdriver import Chrome as ChromeDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from urllib.parse import quote

import yt_dlp
import undetected_chromedriver as uc  # NOQA

from webdriver_manager.chrome import ChromeDriverManager

from models.Playlist import Playlist
from models.Song import Song
from models.Id import get_id


class Api:
    driver: ChromeDriver
    timeout: int

    def __init__(self,
                 timeout: int = 15):
        self.driver = ChromeDriver(service=Service(ChromeDriverManager().install()))
        self.timeout = timeout

        self.chrome_options = selenium.webdriver.chrome.options.Options()
        self.chrome_options.add_argument('start-maximized')
        self.chrome_options.add_argument('--lang=en_US')
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument(
            '--user-agent = Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1')

        self.driver = uc.Chrome(options=self.chrome_options)

        self.setup()

    def get_driver(self):
        return self.driver

    def setup(self):
        self.driver.get('https://music.youtube.com')

        WebDriverWait(self.driver, timeout=self.timeout).until(EC.presence_of_element_located(
            (By.XPATH, '//*[@id="yDmH0d"]/c-wiz/div[1]/div/div/div[2]/div[1]/div['
                       '3]/div[1]/form[2]/div/div/button')))

        self.driver.find_element(By.XPATH,
                                 '//*[@id="yDmH0d"]/c-wiz/div[1]/div/div/div[2]/div[1]/div['
                                 '3]/div[1]/form[2]/div/div/button').click()

    def fetch_song_from_playlist(self, id: str, length: int | str = 'full',
                                 str_output: bool = True):
        result: list[Song | str] = []

        options = selenium.webdriver.chrome.options.Options()
        #  options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        new_driver: selenium.webdriver.Chrome = uc.Chrome(options=options)
        new_driver.get(f'https://music.youtube.com/playlist?list={id}')

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
        for index, song_html in enumerate(song_tags):
            try:
                link_tag = song_html.find_element(By.TAG_NAME, 'a')
                link = link_tag.get_attribute('href')
            except selenium.common.exceptions.NoSuchElementException:
                continue

            if str_output:
                result.append(get_id(link))
            else:
                with yt_dlp.YoutubeDL({'quiet': True,
                                       "external_downloader_args": ['-loglevel', 'panic'],
                                       'extract_flat': True}) as ydl:
                    ydl: yt_dlp.YoutubeDL
                    info = ydl.extract_info(link, download=False)
                try:
                    uploader = info['uploader']
                except KeyError:
                    try:
                        uploader = info['channel']
                    except KeyError:
                        uploader = 'Youtube'

                result.append(
                    Song(id=get_id(link), name=info['title'], creator=uploader, filepath=...))

        new_driver.close()
        return result

    def search_playlist(self, keywords: str, length: int = 5, official: bool = True) -> \
            list[Playlist]:
        """
        ...

        :param keywords:
        :param length:
        :param official:
        :return:
        """
        if official:
            result: list[Playlist] = []

            self.driver.get(f'https://music.youtube.com/search?q={quote(keywords)}')

            WebDriverWait(self.driver, timeout=self.timeout).until(
                EC.presence_of_element_located((
                    By.XPATH, '//*[@id="contents"]/ytmusic-shelf-renderer[5]')))

            expand_button = self.driver.find_element(By.XPATH,
                                                     '//*[@id="contents"]/ytmusic-shelf-renderer[5]/div[6]/a/tp-yt-paper-button')
            try:
                WebDriverWait(self.driver, timeout=self.timeout).until(
                    EC.element_to_be_clickable(
                        (By.XPATH,
                         '//*[@id="contents"]/ytmusic-shelf-renderer[5]/div[6]/a/tp-yt-paper-button')
                    ))
            except selenium.common.exceptions.TimeoutException:
                print('Timeout')
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

            for index, playlist_html in enumerate(playlist_tags):
                link_tag = playlist_html.find_element(By.TAG_NAME, 'a')
                link = link_tag.get_attribute('href')

                ydl_opts = {
                    'extract_flat': True,
                    'quiet': True,
                    "external_downloader_args": ['-loglevel', 'panic']
                }

                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl: yt_dlp.YoutubeDL
                    info = ydl.extract_info(link, download=False)

                    result.append(Playlist(id=get_id(link),
                                           name=info['title'],
                                           songs=self.fetch_song_from_playlist(get_id(link)),
                                           creator=info['uploader']
                                           )
                                  )
            return result

        else:
            ...


if __name__ == '__main__':
    print('Creating API')
    api = Api()
    print('Created API')
    print('Initializing Search')
    x = api.search_playlist('bullshit')
    print('Serch complete')
    print([y.name for y in x])
