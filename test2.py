import requests
from bs4 import BeautifulSoup

headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
               'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
               'accept-encoding': 'gzip, deflate, br',
               'Cache-Control': 'max-age=0',
               'upgrade-insecure-requests': '1',
               'cookie': 'visid_incap_774904=2DAuvjHxSje+T95uUnjT2jFGwloAAAAAQUIPAAAAAADQR73qSha8I2XMelSmpM/N; incap_ses_461_774904=HAKYOHcmbCq5F9I8/M1lBjtGwloAAAAAk3DSZ8xBlHLeuKaHUvHfsg==; incap_ses_625_774904=ZTv7BUsl/DiuoWCqwHKsCJ9GwloAAAAAILjPdjRdH9cOm1vnHOisbw==; _ga=GA1.2.724624907.1522681502; _gid=GA1.2.1409513736.1522681502; permutive-id=5388c047-7f50-4019-8791-ff81ce4ba019; _psegs=%5B1920%2C1930%2C2126%2C2441%2C4848%2C2300%2C3376%5D; _gat=1; _gat_subdomainTracker=1; _gat_streamamp=1; permutive-session=%7B%22session_id%22%3A%22b3cf4245-30cb-43fe-8b3a-0728f6201448%22%2C%22last_updated%22%3A%222018-04-02T15%3A09%3A07.959Z%22%7D',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
               }
all_url = 'https://www.whoscored.com/Matches/1190515/Live/England-Premier-League-2017-2018-Chelsea-Tottenham'  ##开始的URL地址
start_html = requests.get(all_url, headers=headers)  ##使用requests中的get方法来获取all_url(就是：http://www.mzitu.com/all这个地址)的内容 headers为上面设置的请求头、请务必参考requests官方文档解释
print(start_html.text)
Soup = BeautifulSoup(start_html.text, 'lxml')
incidents = Soup.find(id="live-incidents")
tr_list = incidents.tbody.find_all('tr')
print(len(tr_list))
