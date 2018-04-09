from requests_html import HTMLSession

headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Cache-Control': 'max-age=0',
            'upgrade-insecure-requests': '1',
            'cookie': 'visid_incap_774904=2DAuvjHxSje+T95uUnjT2jFGwloAAAAAQUIPAAAAAADQR73qSha8I2XMelSmpM/N; incap_ses_461_774904=HAKYOHcmbCq5F9I8/M1lBjtGwloAAAAAk3DSZ8xBlHLeuKaHUvHfsg==; incap_ses_625_774904=ZTv7BUsl/DiuoWCqwHKsCJ9GwloAAAAAILjPdjRdH9cOm1vnHOisbw==; _ga=GA1.2.724624907.1522681502; _gid=GA1.2.1409513736.1522681502; permutive-id=5388c047-7f50-4019-8791-ff81ce4ba019; _psegs=%5B1920%2C1930%2C2126%2C2441%2C4848%2C2300%2C3376%5D; _gat=1; _gat_subdomainTracker=1; _gat_streamamp=1; permutive-session=%7B%22session_id%22%3A%22b3cf4245-30cb-43fe-8b3a-0728f6201448%22%2C%22last_updated%22%3A%222018-04-02T15%3A09%3A07.959Z%22%7D',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
            }

session = HTMLSession()
r = session.get("https://www.whoscored.com/Matches/1274956/Live/Europe-UEFA-Champions-League-2017-2018-Barcelona-Roma", headers=headers)
r.html.render()
##print(r.html.html)
print(r.html.find("head")[0].html)
incidents = r.html.find("[data-event-satisfier-goalown]")
print(len(incidents))
for inc in incidents:
    print(inc.html)
