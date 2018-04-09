import time
import logging
import sys
import json
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

concern_data_type = ["16", "17", "18", "19"]
url = sys.argv[1]
home_team_name = ""
away_team_name = ""
final_data = []
logger = None
retry_count = 0


def CreateLogger():
    # 创建Logger
    return_logger = logging.getLogger()
    return_logger.setLevel(logging.INFO)

    # 创建Handler

    # 终端Handler
    consoleHandler = logging.StreamHandler()
    consoleHandler.setLevel(logging.INFO)

    # 文件Handler
    logFilePath = time.strftime("%Y-%m-%d", time.localtime()) + '-spider.log'
    fileHandler = logging.FileHandler(logFilePath, mode='a', encoding='UTF-8')
    fileHandler.setLevel(logging.INFO)

    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    consoleHandler.setFormatter(formatter)
    fileHandler.setFormatter(formatter)

    # 添加到Logger中
    return_logger.addHandler(consoleHandler)
    return_logger.addHandler(fileHandler)
    return return_logger

def ParseTeamName(driver):
    global home_team_name, away_team_name
    match_header = driver.find_element_by_id("match-header")
    match_header_tbody = match_header.find_element_by_xpath(".//table/tbody")
    match_team_tr = match_header_tbody.find_element_by_xpath(".//tr[1]")
    home_team_name = match_team_tr.find_element_by_xpath(".//td[1]/a").text
    away_team_name = match_team_tr.find_element_by_xpath(".//td[3]/a").text
    logger.info("home_team_name=" + home_team_name + " away_team_name=" + away_team_name)

def CreateDriver():
    desire = DesiredCapabilities.PHANTOMJS.copy()
    headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
               'Cache-Control': 'max-age=0',
               'upgrade-insecure-requests': '1',
               ##'cookie': 'visid_incap_774904=2DAuvjHxSje+T95uUnjT2jFGwloAAAAAQUIPAAAAAADQR73qSha8I2XMelSmpM/N; incap_ses_461_774904=HAKYOHcmbCq5F9I8/M1lBjtGwloAAAAAk3DSZ8xBlHLeuKaHUvHfsg==; incap_ses_625_774904=ZTv7BUsl/DiuoWCqwHKsCJ9GwloAAAAAILjPdjRdH9cOm1vnHOisbw==; _ga=GA1.2.724624907.1522681502; _gid=GA1.2.1409513736.1522681502; permutive-id=5388c047-7f50-4019-8791-ff81ce4ba019; _psegs=%5B1920%2C1930%2C2126%2C2441%2C4848%2C2300%2C3376%5D; _gat=1; _gat_subdomainTracker=1; _gat_streamamp=1; permutive-session=%7B%22session_id%22%3A%22b3cf4245-30cb-43fe-8b3a-0728f6201448%22%2C%22last_updated%22%3A%222018-04-02T15%3A09%3A07.959Z%22%7D',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
               }
    for key, value in headers.items():
        desire['phantomjs.page.customHeaders.{}'.format(key)] = value

    desire["phantomjs.page.settings.loadImages"] = False
    # 让浏览器不加载图片, 如果网速较慢需要设置代理
    driver = webdriver.PhantomJS(desired_capabilities=desire, service_args=['--load-images=no', '--proxy=127.0.0.1:1080', '--proxy-type=socks5'])
    logger.info("web driver inited!")
    return driver

def GetPage(driver, url):
    driver.set_page_load_timeout(30)
    logger.info("start get page:" + url)
    driver.get(url)
    logger.info("page got")
    ##print(driver.page_source)


def GetGoalType(node):
    if node.get_attribute("data-event-satisfier-goalown") is not None:
        return "own_goal"
    else:
        return "goal"


def GetCardType(node):
    if node.get_attribute("data-event-satisfier-yellowcard") is not None:
        return "yellow_card"
    elif node.get_attribute("data-event-satisfier-voidyellowcard") is not None:
        return "yellow_card"
    elif node.get_attribute("data-event-satisfier-redcard") is not None:
        return "red_card"
    elif node.get_attribute("data-event-satisfier-secondyellow") is not None:
        return "secondyellow"
    else:
        logger.error("GetCardType wrong time:{}:{} player:{}".format(node.get_attribute("data-minute"), node.get_attribute("data-second"), node.get_attribute("data-player-id")))

def ParseIncident(incident, team_name, incident_phase):
    div_nodes = incident.find_elements_by_xpath(".//div[@title]")
    for div_node in div_nodes:
        data_type = div_node.get_attribute("data-type")
        if data_type in concern_data_type:
            player_name = div_node.find_element_by_tag_name("a").text
            sub_div_node = div_node.find_element_by_xpath(".//div[@class='incident-icon']")
            event_time = "{}:{}".format(sub_div_node.get_attribute("data-minute"), sub_div_node.get_attribute("data-second"))
            event_type = ""
            if data_type == "16":
                event_type = GetGoalType(sub_div_node)
            elif data_type == "17":
                event_type = GetCardType(sub_div_node)
            elif data_type == "18":
                event_type = "substitution_exit"
            elif data_type == "19":
                event_type = "substitution_enter"

            incident_data = {"host_team": home_team_name, "away_team": away_team_name, "team": team_name, "player": player_name, "time": event_time, "type": event_type, "phase": incident_phase}
            final_data.append(incident_data)


def ParseIncidentPhase(event_time):
    if event_time == "PEN'":
        return "penalty_shootout"
    else:
        event_time = event_time[:-1]##去掉最后一个'
        tmp_index = event_time.find("+")
        if tmp_index >= 0:
            event_time = event_time[0, tmp_index]

        minute = int(event_time)
        if minute <= 45:
            return "first_half"
        elif minute <= 90:
            return "second_half"
        elif minute <= 105:
            return "overtime_first_half"
        elif minute <= 120:
            return "overtime_second_half"
        else:
            logger.error("ParseIncidentPhase Error event_time={}, minute={}".format(event_time, minute))
            return "wrong_time"


def ParsePlayers(bench_node, team_name, lineup_type):
    player_nodes = bench_node.find_elements_by_xpath(".//div[@class='player-name-wrapper' and @title]")
    ##logger.info("team:{} has {}  {} players".format(team_name, len(player_nodes), lineup_type))
    for node in player_nodes:
        player_name = node.get_attribute("title")
        bench_player_data = {"host_team": home_team_name, "away_team": away_team_name, "team": team_name,
                         "player": player_name, "time": "00:00", "type": lineup_type, "phase": "first_half"}
        final_data.append(bench_player_data)


#分析阵容
def ParseMatchPlayers(driver):
    #替补
    home_bench = driver.find_element_by_xpath("//div[@class='bench' and @data-field='home']")
    away_bench = driver.find_element_by_xpath("//div[@class='bench' and @data-field='away']")
    ParsePlayers(home_bench, home_team_name, "alternate")
    ParsePlayers(away_bench, away_team_name, "alternate")
    #首发
    home_starting = driver.find_element_by_xpath("//div[@class='pitch-field' and @data-field='home']")
    away_starting = driver.find_element_by_xpath("//div[@class='pitch-field' and @data-field='away']")
    ParsePlayers(home_starting, home_team_name, "starting_lineup")
    ParsePlayers(away_starting, away_team_name, "starting_lineup")


#分析事件
def ParseMatchIncidents(driver):
    elem = driver.find_element_by_id("live-incidents")
    tbody_elem = elem.find_element_by_xpath(".//div/table/tbody")
    tr_elems = tbody_elem.find_elements_by_xpath(".//tr")
    logger.info("live-incidents count=" + str(len(tr_elems)))
    for detail_elem in tr_elems:
        home_incident = detail_elem.find_element_by_xpath(".//*[@class='key-incident home-incident']")
        away_incident = detail_elem.find_element_by_xpath(".//*[@class='key-incident away-incident']")
        incident_time = detail_elem.find_element_by_xpath(".//*[@class='minute rc box']")
        incident_phase = ParseIncidentPhase(incident_time.text)
        ParseIncident(home_incident, home_team_name, incident_phase)
        ParseIncident(away_incident, away_team_name, incident_phase)


def CheckMatchEnd(driver):
    match_report_node = driver.find_element_by_xpath("//a[contains(text(), 'Match') and contains(text(), 'Report')]")
    if match_report_node.get_attribute("class") == "inactive":
        return False
    else:
        return True


class MatchNotEndError(RuntimeError):
    def __init__(self):
        pass


def LoadPage(driver):
    GetPage(driver, url)
    '''
    if CheckMatchEnd(driver) is False:
        raise MatchNotEndError()
    else:
        logger.info("Match End")
    '''

    ParseTeamName(driver)
    ParseMatchPlayers(driver)
    ParseMatchIncidents(driver)
    logger.info("final_data={}".format(final_data))

def PostResult():
    r = requests.post('http://httpbin.org/post', json=final_data)
    logger.info("Post status_code= {}".format(r.status_code))


CheckMatchEndInterval = 300
RetryInterval = 10
SpiderTimeOut = 8 * 3600

logger = CreateLogger()
start_time = time.time()
while time.time() - start_time < SpiderTimeOut:
    try:
        retry_count += 1
        logger.info("try times:{}".format(retry_count))
        driver = CreateDriver()
        LoadPage(driver)
    except MatchNotEndError:
        driver.quit()
        logger.info("Match is not end yet!!, sleep for a while")
        time.sleep(CheckMatchEndInterval)
    except Exception as e:
        driver.quit()
        logger.error("Exception :{}".format(e))
        import traceback
        traceback.print_exc()
        time.sleep(RetryInterval)
    else:
        logger.info("Load Page Sccessed!!!")
        PostResult()
        break
else:
    logger.error("Spider Time Out")

driver.quit()
logging.shutdown()



