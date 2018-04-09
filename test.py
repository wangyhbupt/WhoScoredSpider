import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import os

##headers = {'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1"}##浏览器请求头（大部分网站没有这个请求头会报错、请务必加上哦）
##all_url = 'https://www.whoscored.com/Matches/1005321/Live/International-FIFA-World-Cup-2016-2017-France-Belarus#'  ##开始的URL地址
##start_html = requests.get(all_url)  ##使用requests中的get方法来获取all_url(就是：http://www.mzitu.com/all这个地址)的内容 headers为上面设置的请求头、请务必参考requests官方文档解释
##print(start_html.text)
##driver = webdriver.PhantomJS()
##all_url = 'https://www.zhihu.com/explore'  ##开始的URL地址
##driver.get(all_url)
##print(driver.page_source)

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36' }

##for key in headers:
    ##webdriver.DesiredCapabilities.PHANTOMJS['phantomjs.page.customHeaders.{}'.format(key)] = headers[key]
phantomjs_path = r"E:\BaiduYunDownload\chromedriver_win32\chromedriver.exe"
##driver = webdriver.Chrome()
driver = webdriver.Chrome(executable_path=phantomjs_path)
driver.get("https://www.whoscored.com/Matches/1005321/Live/International-FIFA-World-Cup-2016-2017-France-Belarus#")
elem = driver.find_element_by_id("live-incidents-wrapper")
table_elem = elem.find_element_by_xpath(".//table")
tbody_elem = table_elem.find_element_by_xpath(".//tbody")
tr_elems = tbody_elem.find_elements_by_xpath(".//tr")
print("children count=" + str(len(tr_elems)))
for detail_elem in tr_elems:
    print(detail_elem.text)

