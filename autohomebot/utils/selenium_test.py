import time
from selenium import webdriver

chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--headless')
# prefs ={
#      'profile.default_content_setting_values': {
#         'images': 2,
#         # 'javascript':2
#     }
# }
# chrome_options.add_experimental_option('prefs', prefs)
chrome_options.add_argument('--ignore-certificate-errors')
browser = webdriver.Chrome(chrome_options=chrome_options,
                           # executable_path=path_to_chromedriver
                           )


url = "https://www.baidu.com/"
browser.get(url)
time.sleep(3)
browser.close()
time.sleep(3)
browser.get(url)