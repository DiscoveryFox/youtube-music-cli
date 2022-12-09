import time

import fetch_feed
import selenium
import undetected_chromedriver as uc

""" Deprecated. 
chrome_driver = selenium.webdriver.chrome.service.Service('./chromedriver.exe')
driver = selenium.webdriver.Chrome(service=chrome_driver, options=chrome_options)
"""

chrome_options = selenium.webdriver.chrome.options.Options()
chrome_options.add_argument('start-maximized')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--lang=en_US')
chrome_options.add_argument('--user-agent = Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1')

undetected_driver = uc.Chrome(options=chrome_options)

youtubeMusic = fetch_feed.YoutubeMusic(undetected_driver)

search_result = youtubeMusic.search('paradise coldplay')

print('Starting Playing')
youtubeMusic.add_song(search_result[1])
youtubeMusic.add_song(youtubeMusic.search('999 (Remix)')[0])
youtubeMusic.play()
print('Started Playing')
time.sleep(5)
print('Still Playing')
time.sleep(10)
youtubeMusic.skip()