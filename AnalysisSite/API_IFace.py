#Imports
try:
    import urllib.request as urllib2
except ImportError:
    import urllib2

import json
from dateutil import parser
from datetime import date
import time
from Classes import Play 
import pickle

class Sports_API(object):
    """Does the interface with the """
    def __init__(self, access, version):
        super(Sports_API, self).__init__()
        self.access = access
        self.version = version
        self.api_key = "hucdepxvc9e64g2ft4n964z8"

    def get_weekly_schedule(self, year, season_type, season_week):
        """
        Format:
        http(s)://api.sportsdatallc.org/nfl-[access_level][version]/[year]/[nfl_season]/[nfl_season_week]/schedule.[format]?api_key=[your_api_key]
        
        Variables:
        [access_level] = Real-Time (rt), Premium (p), Standard (s), Basic (b), Trial (t)
        [version] = whole number (sequential, starting with the number 1)
        [year] = yyyy
        [nfl_season] = Preseason (PRE), Regular Season (REG), Postseason (PST)
        [nfl_season_week] = 1 - 17 (Week 0 of Preseason is Hall of Fame game)
        [format] = xml, json
        """
        base = "http://api.sportsdatallc.org/nfl-{acc}{ver}/{year}/{seas}/{week}/schedule.json?api_key={key}"
        request = base.format(acc=self.access, ver=self.version, year=year, seas=season_type, week=season_week, key=self.api_key)
        print("Sending request: " + request)
        resp = urllib2.urlopen(request).read()
        print(resp)

    def get_season_schedule(self, year, season_type):
        """
        http(s)://api.sportsdatallc.org/nfl-[access_level][version]/[year]/[nfl_season]/schedule.[format]?api_key=[your_api_key]
        """
        base = "http://api.sportsdatallc.org/nfl-{acc}{ver}/{year}/{seas}/schedule.json?api_key={key}"
        request = base.format(acc=self.access, ver=self.version, year=year, seas=season_type, key=self.api_key)
        print("Sending request: " + request)
        resp = urllib2.urlopen(request).read()        
        return resp

    def parse_schedule(self, schedule, year, season_type):
        games = []
        weeks = schedule["weeks"]
        for i in range(len(weeks)):
            week = weeks[i]
            n = len(week)            
            for game in week["games"]:
                games.append(Game(game, i+1, season_type, year))
        return games

#An object to represent a given game
class Game(object):
    """docstring for Game"""
    def __init__(self, rep, week, season_type, year):
        super(Game, self).__init__()
        self.id = rep["id"].replace("-","")
        self.home = rep["home"]
        self.away = rep["away"]
        self.date = parser.parse(rep["scheduled"])
        self.week = week
        self.season_type = season_type
        self.year = year
        self.raw = rep

    def get_game_feed(self, API):
        """
        http(s)://api.sportsdatallc.org/nfl-[access_level][version]/[year]/[nfl_season]/[nfl_season_week]/[away_team]/[home_team]/pbp.[format]?api_key=[your_api_key]
        """
        base = "http://api.sportsdatallc.org/nfl-{acc}{ver}/{year}/{seas}/{week}/{away}/{home}/pbp.json?api_key={key}"
        request = base.format(acc=API.access, ver=API.version, year=self.year, seas=self.season_type, week=self.week, away=self.away, home=self.home, key=API.api_key)
        print("Sending request: " + request)
        resp = urllib2.urlopen(request).read()
        return resp

    def __repr__(self):
        return "{} on  {}: {} vs {}".format(self.date.strftime('%Y-%m-%d %H:%M'), self.raw['broadcast']['network'], self.home, self.away)
        

#----Main Methods
#--------------------
def get_schedule(API, year, season_type):
    res = API.get_season_schedule(year, season_type)
    file_path = "../"
    with open(file_path + 'schedule', 'w') as f:
        f.write(res)


def get_game_data(API, year, season_type):
    file_path = "../"
    with open(file_path + 'schedule', 'r') as f:
        res = f.read()

    obj = json.loads(res)
    games = API.parse_schedule(obj, year, season_type)    
    for game in games:
        with open(file_path + "REG/" + "{}".format(game.id), 'w') as f:
            f.write(game.get_game_feed(API))
            time.sleep(1)

def main():
    API = Sports_API("t", "1")

    file_path = "./Games/CAR_ARI"
    with open(file_path, 'r') as f:
        obj = json.loads(f.read())
    
    score = {obj["home_team"]["id"]:0, obj["away_team"]["id"]:0}

    plays = []

    for i,quarter in enumerate(obj["quarters"]):
        pbp = quarter["pbp"]        
        for posession in pbp:
            if(not posession["type"] == 'drive'):
                continue
            team = posession["team"]
            
            for play in posession["actions"]:
                p = Play(play, i, team, score)
                if(p.isdata):
                    plays.append(p)

    with open("sample_plays", 'wb') as f:        
        pickle.dump(plays, f)

if(__name__ == "__main__"):
    #main()
    API = Sports_API("t", "1")
    get_schedule(API, 2014, "REG")
    time.sleep(1)
    get_game_data(API, "2014", "REG")

