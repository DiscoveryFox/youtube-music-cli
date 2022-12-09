import selenium.webdriver
import selenium.webdriver.chrome.service
import selenium.webdriver.chrome.options
import fetch_feed

chrome_driver = selenium.webdriver.chrome.service.Service('./chromedriver.exe')

chrome_options = selenium.webdriver.chrome.options.Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument('--lang=en_US')

driver = selenium.webdriver.Chrome(service=chrome_driver, options=chrome_options)

youtubeMusic = fetch_feed.YoutubeMusic(driver)
print(youtubeMusic.search('last christmas'))

while True:
    ...
