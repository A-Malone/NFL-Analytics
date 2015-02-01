from django.http import HttpResponse
from django.shortcuts import render
import os
import sys
import json
import pickle
import copy

print(sys.path)
from API_IFace import Game, Sports_API, get_schedule
from Classes import *
from django.views.decorators.csrf import *


#----Init
API = Sports_API("t", "1")

#----Globals
plays = []
score = {}
teams = []
seq = 0

#----Globals
plays_file = open('sample_plays','rb')
play_hashtable = pickle.load(plays_file)


#----Functions
def get_plays(obj):
    score = {obj["home_team"]["id"]:0, obj["away_team"]["id"]:0}

    plays = []

    for i,q in enumerate(obj["quarters"]):        
        pbp = q["pbp"]        
        for posession in pbp:
            if(not posession["type"] == 'drive'):
                continue
            team = posession["team"]
            
            for play in posession["actions"]:
                p = Play(play, i, team, score)
                if(p.isdata):
                    plays.append(p)
                    score = copy.deepcopy(p.score)
    return plays

def load_schedule():
    file_path = "../"
    with open(file_path + 'schedule', 'r') as f:
        res = f.read()

    obj = json.loads(res)
    games = API.parse_schedule(obj, 2014, "PST")
    return games

#TODO: Complete this
@csrf_exempt
def get_play(request, game_id):
    global score, teams, seq, plays

    play = plays[seq]    

    #Update scores    
    team = teams.index(play.offense)
    score[teams[team]] = play.score[teams[team]]
    score[teams[1-team]] = play.score[teams[1-team]]
    diff = score[teams[team]] - score[teams[1-team]]

    to_front = {"time":play.time, "score":[play.score[teams[0]],play.score[teams[1]]], "offense":play.offense, "dist":play.position, "yfd":play.distance_to_first, "num":play.sequence, "summ":play.summary}

    try:
        out_data = update(play_hashtable, int(play.start_down) , int(play.distance_to_first), int(play.time.split(":")[0]), int(play.quarter), int(play.position), int(diff), teams[team])    
        to_front["pred"] = out_data
    except:
        to_front["pred"] = "Insufficient data"


    out_json = json.dumps(to_front)
    seq+=1
    return HttpResponse(out_json, content_type='application/json')
    

def index(request):
    global API
    games = load_schedule()

    context_dict = {'games': games}
    return render(request, 'PlayBook/index.html', context_dict)

def viewGame(request, game_id):
    global plays, score, teams
    file_path = "../"
    with open(file_path + 'Games/' + str(game_id), 'r') as f:
        res = f.read()

    obj = json.loads(res)
    plays = get_plays(obj)
    teams = [obj["home_team"]["id"], obj["away_team"]["id"]]
    score = {teams[0]:0, teams[1]:0}
    
    context_dict = {'home':obj["home_team"]["name"], 'away':obj["away_team"]["name"], 'gameid':json.dumps(obj["id"].replace("-","")), 'last_play':int(len(plays))}

    return render(request, 'PlayBook/game.html', context_dict)
