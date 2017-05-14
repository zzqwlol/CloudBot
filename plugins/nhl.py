import datetime
import pytz

import requests

from cloudbot import hook

BASE_URL = "https://statsapi.web.nhl.com/api/v1/schedule"
SCHEDULE_PATH = "?startDate={}&endDate={}&timeZone=EST&teamId={}"
FORMAT = "%Y-%m-%d"

TEAMS = {
    "ANA": "24",
    "ARI": "53",
    "BOS": "6",
    "BUF": "7",
    "CAR": "12",
    "CBJ": "29",
    "CGY": "20",
    "CHI": "16",
    "COL": "21",
    "DAL": "25",
    "DET": "17",
    "EDM": "22",
    "FLA": "13",
    "LAK": "26",
    "MIN": "30",
    "MTL": "8",
    "NJD": "1",
    "NSH": "18",
    "NYI": "2",
    "NYR": "3",
    "OTT": "9",
    "PHI": "4",
    "PIT": "5",
    "SJS": "28",
    "STL": "19",
    "TBL": "14",
    "TOR": "10",
    "VAN": "23",
    "WPG": "52",
    "WSH": "15"
}


@hook.command("nhl")
def nhl(text, message):
    """nhl [team abbr] [today] [tomorrow] [yyyy/mm/dd] - display NHL games."""
    inp = text.strip().lower()
    date = datetime.datetime.now(pytz.timezone("US/Eastern"))
    search_date = date.strftime(FORMAT)
    game = ("\x1F{}\x1F ({}) vs. \x1F{}\x1F ({}) @ \x1F{}\x1F (EST) | "
            "State: \x1F{}\x1F")

    if inp == "today":
        url = BASE_URL + SCHEDULE_PATH.format(search_date, search_date, "")
    elif inp == "tomorrow":
        tomorrow = date + datetime.timedelta(days=1)
        search_date = tomorrow.strftime(FORMAT)
        url = BASE_URL + SCHEDULE_PATH.format(search_date, search_date, "")
    elif inp.startswith("201"):
        search_date = inp
        url = BASE_URL + SCHEDULE_PATH.format(inp, inp, "")
    elif inp.upper() in TEAMS.keys():
        url = BASE_URL + SCHEDULE_PATH.format(search_date, search_date,
                                              TEAMS[inp.upper()])
    else:
        return "None found."

    req = requests.get(url)

    if req.status_code != requests.codes.ok:
        return "NHL API returned a non-200 HTTP status code: {}".format(
                req.status_code)

    data = req.json()

    if data["totalGames"] == 0:
        return "No games found for {}.".format(search_date)

    total_games = data["totalGames"]
    game_data = data["dates"][0]["games"]
    schedule = "There's \x1F{}\x1F NHL game{} scheduled for \x1F{}\x1F:".format(
               total_games, "s" if total_games > 1 else "", search_date)

    games = [game.format(game_data[i]["teams"]["away"]["team"]["name"],
             game_data[i]["teams"]["away"]["score"],
             game_data[i]["teams"]["home"]["team"]["name"],
             game_data[i]["teams"]["home"]["score"],
             game_data[i]["gameDate"].split("T")[1][:5],
             game_data[i]["status"]["detailedState"])
             for i in range(total_games)]

    message(schedule)

    for i in games:
        message(i)

#  vim: set ts=4 sw=4 tw=79 et :
