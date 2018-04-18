import requests
import json
from bs4 import BeautifulSoup

headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
               'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
               'accept-encoding': 'gzip, deflate, br',
               'Cache-Control': 'max-age=0',
               'upgrade-insecure-requests': '1',
               'cookie': 'visid_incap_774904=2DAuvjHxSje+T95uUnjT2jFGwloAAAAAQUIPAAAAAADQR73qSha8I2XMelSmpM/N; incap_ses_461_774904=HAKYOHcmbCq5F9I8/M1lBjtGwloAAAAAk3DSZ8xBlHLeuKaHUvHfsg==; incap_ses_625_774904=ZTv7BUsl/DiuoWCqwHKsCJ9GwloAAAAAILjPdjRdH9cOm1vnHOisbw==; _ga=GA1.2.724624907.1522681502; _gid=GA1.2.1409513736.1522681502; permutive-id=5388c047-7f50-4019-8791-ff81ce4ba019; _psegs=%5B1920%2C1930%2C2126%2C2441%2C4848%2C2300%2C3376%5D; _gat=1; _gat_subdomainTracker=1; _gat_streamamp=1; permutive-session=%7B%22session_id%22%3A%22b3cf4245-30cb-43fe-8b3a-0728f6201448%22%2C%22last_updated%22%3A%222018-04-02T15%3A09%3A07.959Z%22%7D',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
               }
refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI1YWQ1YTM5MjM0OGFhNzA3MGQwNjg3MzAiLCJpYXQiOjE1MjM5NTA3NDR9.uBMD5JOpf7qM20b2ojfIdRGsLV8hCRvH8BmAamd9FWw"
access_token = ""

home_team_name=''
away_team_name=''
def GetAccessToken():
    get_url = "https://api.sportdeer.com/v1/accessToken?refresh_token={}".format(refresh_token)
    token_response = requests.get(get_url)
    print(token_response.text)

GetAccessToken()
all_url = 'https://api.sportdeer.com/v1/fixtures/30938?populate=lineups&populate=events&access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI1YWQ1YTM5MjM0OGFhNzA3MGQwNjg3MzAiLCJhY2Nlc3NfbGV2ZWwiOjEsImlhdCI6MTUyNDA0MTA2NCwiZXhwIjoxNTI0MDQyODY0fQ.RvqgouPRTAuGeSyQl0nend2yb8GIVlEJHgPyaPyE_8s'  ##开始的URL地址
start_html = requests.get(all_url)  ##使用requests中的get方法来获取all_url(就是：http://www.mzitu.com/all这个地址)的内容 headers为上面设置的请求头、请务必参考requests官方文档解释
print(start_html.text)
data = json.loads(start_html.text)
fixture = data["docs"][0]
home_team_name = fixture["team_season_home_name"]
away_team_name = fixture["team_season_away_name"]
events = fixture["events"]
print("---------------Event Start-------------")
for event in data["docs"][0]["events"]:
    print("#############")
    print("event id={} desc={}".format(event["_id"], event))

