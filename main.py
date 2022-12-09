import time

import YoutubeConnector

""" Deprecated. 
chrome_driver = selenium.webdriver.chrome.service.Service('./chromedriver.exe')
driver = selenium.webdriver.Chrome(service=chrome_driver, options=chrome_options)
"""

with YoutubeConnector.YoutubeMusic(timeout=10) as youtubeMusic:
    query_result = youtubeMusic.search_official_playlists('deutschrap', length=5)

    print('Starting download')
    youtubeMusic.add_playlist(query_result[0], length=10)

    print('Download Done now continue')

    search_result = youtubeMusic.search_song('paradise coldplay')

    print('Starting Playing')
    youtubeMusic.add_song(search_result[1])
    youtubeMusic.play()
    youtubeMusic.add_song(youtubeMusic.search_song('999 (Remix)')[0])
    while True:
        x = input('Skip Y/n | Stop S:')
        if x == 'S':
            youtubeMusic.stop()
        else:
            youtubeMusic.skip()

