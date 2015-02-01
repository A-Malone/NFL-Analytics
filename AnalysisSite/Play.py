import re

class Play:
	'''
	This class stores data for one NFL regulation play. Data scraped from Sport Data API. Variable Descriptions:
	Offense (str) offensive team's name
	Defense (str) defensive team's name
	start_down (int) Down when play starts
	distance_to_first (int) Distance to first down
	end_down (int) Down when play ends
	end_distance_to_first (int) Distance to first down at end of play
	play_type (int) Run (0) or Pass (1)
	play_type_detail (int) If run: Left (0), Middle (1), Right (2). If throw: Short (<5) (0), Medium (5-15) (1), Long (>15) (2)
	turnover (int) No turnover (0), Turnover (1)
	position (int) Position on field at beggining of play (0-100). 0 Corresponds to own endzone, 100 opponents endzone
	score_offense (int) Current number of points that the offense has
	score_defense (int) Current number of points that the defense has
	time (int) number of minutes left in quarter
	quarter (int) Quarter that the play occured in (1-4)
	player (str) Player name identified by play-by-play
	'''

	def __init__(self, json, quarter, posession, score):	

		#Skips coin tosses and other non-play events		
		if(json["type"] != "play"):
			print("Skipping: " + json["type"])
			self.isdata = False
			return None
		if(json["play_type"] == "kick"):
		 	print("Skipping: " + json["play_type"])
			self.isdata = False
			return None
		

		#Flag to signal this is useful data
		self.isdata = True

		self.sequence = int(json["sequence"])

		#Sets the score
		self.score = score
		
		#From the super-json
		self.offense = posession
		#self.defence = defence

		#Irrelevant of play type
		self.play_type = json["play_type"]
		self.start_down = json["down"] if "down" in json.keys() else None
		self.time = json["clock"] if "clock" in json.keys() else None

		if(json["play_type"] == "extrapoint" or json["play_type"] == "fieldgoal"):
			if(json["summary"].lower().endswith("is good.")):
				self.score[self.offense] += 1
		else:
			#Runs and passes
			self.formation = json["formation"] if "formation" in json.keys() else None
			self.distance_to_first = int(json["yfd"]) if "yfd" in json.keys() else None
			self.direction = json["direction"] if "direction" in json.keys() else None

			self.position = int(json["yard_line"]) if posession==json["side"] else 100-int(json["yard_line"])
			
			match = re.search(r'for [-0-9]+ yard', json['summary'])
			if(match):
				self.distance = int(re.sub(r'[a-z]*',"", match.group()))
			else:
				self.distance = 0
			
			self.passing_distance = None
			if(json["play_type"] == "pass"):	#Passes
				self.passing_distance = json["distance"] if "distance" in json.keys() else None
				if("incomplete" in json['summary']):
					self.complete = False
				else:
					self.complete = True					
			
			if("touchdown" in json["summary"]):
				self.score[self.offense] += 6		
		
		if("INTERCEPTED" in json["summary"]):
			self.turnover = True
		else:
			self.turnover = False
		
		self.quarter = quarter
		self.players = [(int(player["jersey"]), player["name"]) for player in json["participants"]] if "participants" in json.keys() else None
		

	def __lt__(self,other):
		return self.distance_to_first <= other.distance_to_first

	def __str__(self):
		string = 'Offense:'
		string += self.offense
		string += ' Down:'
		string += str(self.start_down)
		string += ' To go:'
		string += str(self.distance_to_first)
		string += ' Play:'
		string += self.play_type
		string += ' Direction:'
		string += self.direction
		string += ' Distance gained:'
		string += int(self.distance)
		return string
