from django.http import HttpResponse
from django.shortcuts import render
import os
import sys
import json

print(sys.path)
from API_IFace import Game, Sports_API, get_schedule
from Classes import *
from django.views.decorators.csrf import *


#----Init
API = Sports_API("t", "1")


#----Functions
def get_plays(obj):
    score = {obj["home_team"]["id"]:0, obj["away_team"]["id"]:0}

    plays = []

    for i,q in enumerate(obj["quarters"]):
        quarter = []
        pbp = q["pbp"]        
        for posession in pbp:
            if(not posession["type"] == 'drive'):
                continue
            team = posession["team"]
            
            for play in posession["actions"]:
                p = Play(play, i, team, score)
                if(p.isdata):
                    quarter.append(p)
        plays.append(quarter)
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
    #print(request)    
    data = json.loads(request.body)    


    
    out_json = json.dumps(out_data)
    return HttpResponse(out_json, content_type='application/json')
    

def index(request):
    global API
    games = load_schedule()

    context_dict = {'games': games}
    return render(request, 'PlayBook/index.html', context_dict)

def viewGame(request, game_id):
    file_path = "../"
    with open(file_path + 'Games/' + str(game_id), 'r') as f:
        res = f.read()

    obj = json.loads(res)
    
    context_dict = {'home':obj["home_team"]["name"], 'away':obj["away_team"]["name"], 'gameid':json.dumps(obj["id"].replace("-","")), 'game_json':json.dumps(obj["quarters"])}

    return render(request, 'PlayBook/game.html', context_dict)
