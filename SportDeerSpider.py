import time
import logging
import sys
import requests
import json

#检查比赛结束的间隔
CheckMatchEndInterval = 300
#发生异常是的重试间隔
RetryInterval = 10
#爬虫启动后的总超时
SpiderTimeOut = 8 * 3600
#页面加载超时，如果服务器网络较慢，就要设置长一点
PageLoadTimeOut = 90

refresh_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI1YWQ1YTM5MjM0OGFhNzA3MGQwNjg3MzAiLCJpYXQiOjE1MjM5NTA3NDR9.uBMD5JOpf7qM20b2ojfIdRGsLV8hCRvH8BmAamd9FWw"
access_token = ""
fixture_id = sys.argv[1]
url = 'https://api.sportdeer.com/v1/fixtures/30938?populate=lineups&populate=events&access_token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VySWQiOiI1YWQ1YTM5MjM0OGFhNzA3MGQwNjg3MzAiLCJhY2Nlc3NfbGV2ZWwiOjEsImlhdCI6MTUyNDA0MTA2NCwiZXhwIjoxNTI0MDQyODY0fQ.RvqgouPRTAuGeSyQl0nend2yb8GIVlEJHgPyaPyE_8s'
home_team_name = ""
away_team_name = ""
fixture_data = {}
final_data = []
player_nams = {}
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
    match_name = fixture_id
    logFilePath = time.strftime("%Y-%m-%d", time.localtime()) + '-' + match_name + '-spider.log'
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

def ParseTeamName():
    global home_team_name, away_team_name
    home_team_name = fixture_data["team_season_home_name"]
    away_team_name = fixture_data["team_season_away_name"]
    logger.info("home_team_name=" + home_team_name + " away_team_name=" + away_team_name)


def GetAccessToken():
    global access_token
    get_url = "https://api.sportdeer.com/v1/accessToken?refresh_token={}".format(refresh_token)
    token_response = requests.get(get_url)
    token_response.close()
    if token_response.status_code != 200:
        logger.error("GetAccessToken Response Error:{}".format(token_response.status_code))
        raise ResponseError(token_response.status_code)
    else:
        logger.info(token_response.text)
        data = json.loads(token_response.text)
        access_token = data["new_access_token"]


def GetPage():
    global url, fixture_data
    url = 'https://api.sportdeer.com/v1/fixtures/{}?populate=lineups&populate=events&access_token={}'.format(fixture_id, access_token)
    logger.info("start get page:" + url)
    response = requests.get(url)
    response.close()
    logger.info("page got")
    if response.status_code != 200:
        logger.error("GetPage Response Error:{}".format(response.status_code))
        raise ResponseError(response.status_code)
    else:
        data = json.loads(response.text)
        fixture_data = data["docs"][0]


    ##print(driver.page_source)


def ParseGoalIncident(event_info, event_time, event_phase, team_name):
    event_type = "goal"
    if "goal_type_code" in event_info.keys():
        if event_info["goal_type_code"] == "og":
            event_type = "own_goal"

    player_name = ""
    player_team_season_id = event_info["id_team_season_scorer"]
    if player_team_season_id in player_nams.keys():
        player_name = player_nams.get(player_team_season_id)
    else:
        logger.error("ParseGoalIncident can't find player name player_team_season_id={}".format(player_team_season_id))

    incident_data = {"host_team": home_team_name, "away_team": away_team_name, "team": team_name, "player": player_name,
                     "time": event_time, "type": event_type, "phase": event_phase}
    final_data.append(incident_data)


def ParseCardIncident(event_info, event_time, event_phase, team_name):
    player_name = ""
    player_team_season_id = event_info["id_team_season_player"]
    if player_team_season_id in player_nams.keys():
        player_name = player_nams.get(player_team_season_id)
    else:
        logger.error("ParseCardIncident can't find player name player_team_season_id={}".format(player_team_season_id))

    event_type = "yellow_card"
    if event_info["card_type"] == "y":
        event_type = "yellow_card"
    elif event_info["card_type"] == "r":
        event_type = "red_card"
    elif event_info["card_type"] == "y2":
        event_type = "secondyellow"
    else:
        logger.error("ParseCardIncident wrong time:{} player:{}".format(event_time, player_name))

    incident_data = {"host_team": home_team_name, "away_team": away_team_name, "team": team_name, "player": player_name,
                     "time": event_time, "type": event_type, "phase": event_phase}
    final_data.append(incident_data)


def ParseSubStIncident(event_info, event_time, event_phase, team_name):
    player_in_name = ""
    player_out_name = ""
    player_in_id = event_info["id_team_season_player_in"]
    player_out_id = event_info["id_team_season_player_out"]
    if player_in_id in player_nams.keys():
        player_in_name = player_nams.get(player_in_id)
    else:
        logger.error("ParseSubStIncident can't find player name player_in_id={}".format(player_in_id))

    if player_out_id in player_nams.keys():
        player_out_name = player_nams.get(player_out_id)
    else:
        logger.error("ParseSubStIncident can't find player name player_out_id={}".format(player_out_id))

    incident_in_data = {"host_team": home_team_name, "away_team": away_team_name, "team": team_name, "player": player_in_name,
                     "time": event_time, "type": "substitution_enter", "phase": event_phase}
    final_data.append(incident_in_data)
    incident_out_data = {"host_team": home_team_name, "away_team": away_team_name, "team": team_name, "player": player_out_name,
                        "time": event_time, "type": "substitution_exit", "phase": event_phase}
    final_data.append(incident_out_data)



def ParseIncidentPhase(event_time):
        minute = int(event_time)
        if minute <= 45:
            return "first_half"
        elif minute <= 90:
            return "second_half"
        elif minute <= 105:
            return "overtime_first_half"
        elif minute <= 120:
            return "overtime_second_half"
        elif minute > 120:
            return "penalty_shootout"
        else:
            logger.error("ParseIncidentPhase Error event_time={}, minute={}".format(event_time, minute))
            return "wrong_time"


#分析阵容
def ParseMatchPlayers():
    lineup_data = fixture_data["lineups"]
    for player_info in lineup_data:
        player_nams[player_info["id_team_season_player"]] = player_info["player_name"]
        lineup_type = "starting_lineup"
        if player_info["is_startingXI"] is False:
            lineup_type = "alternate"

        player_data = {"host_team": home_team_name, "away_team": away_team_name, "team": player_info["team_name"],
                       "player": player_info["player_name"], "time": "00:00", "type": lineup_type,
                       "phase": "first_half"}
        final_data.append(player_data)


#分析事件
def ParseMatchIncidents():
    event_data = fixture_data["events"]
    logger.info("match incidents count={}".format(len(event_data)))
    for event_info in event_data:
        event_time = int(event_info["elapsed"])
        if "elapsed_plus" in event_info.keys():
            event_time += int(event_info["elapsed_plus"])
        event_phase = ParseIncidentPhase(event_info["elapsed"])
        team_name = event_info["team_name"]
        original_event_type = event_info["type"]
        if original_event_type == "goal":
            ParseGoalIncident(event_info, "{}:00".format(event_time), event_phase, team_name)
        elif original_event_type == "card":
            ParseCardIncident(event_info,  "{}:00".format(event_time), event_phase, team_name)
        elif original_event_type == "subst":
            ParseSubStIncident(event_info,  "{}:00".format(event_time), event_phase, team_name)
        else:
            continue




def CheckMatchEnd():
    if "game_ended_at" in fixture_data.keys():
        return True
    else:
        return False


class MatchNotEndError(RuntimeError):
    def __init__(self):
        pass


class ResponseError(RuntimeError):
    def __init__(self, reponse_code):
        self.response_code = reponse_code



def LoadPage():
    GetAccessToken()
    GetPage()
    if CheckMatchEnd() is False:
        raise MatchNotEndError()
    else:
        logger.info("Match End")

    ParseTeamName()
    ParseMatchPlayers()
    ParseMatchIncidents()
    logger.info("final_data={}".format(final_data))

def PostResult():
    r = requests.post('http://httpbin.org/post', json=final_data)
    logger.info("Post status_code= {}".format(r.status_code))


logger = CreateLogger()
start_time = time.time()
while time.time() - start_time < SpiderTimeOut:
    try:
        retry_count += 1
        logger.info("try times:{}".format(retry_count))
        LoadPage()
    except MatchNotEndError:
        logger.info("Match is not end yet!!, sleep for a while")
        time.sleep(CheckMatchEndInterval)
    except Exception as e:
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

logging.shutdown()



