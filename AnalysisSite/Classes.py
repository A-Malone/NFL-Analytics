import re
import math as m
import numpy as np

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
#			print("Skipping: " + json["type"])
			self.isdata = False
			return None
		if(json["play_type"] == "kick"):
#		 	print("Skipping: " + json["play_type"])
			self.isdata = False
			return None
		
		self.sequence = json["sequence"]
		#Flag to signal this is useful data
		self.isdata = True

		#Sets the score
		self.score = score
		
		#From the super-json
		self.offense = posession

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

		''' ADDED TO Play CLASS '''

		teams = self.score.keys()
		if(teams[0] == posession):
			teams.pop(0)
		else:
			teams.pop(1)
		defense = teams[0]
		self.score_diff = self.score[self.offense] - self.score[defense]

		''' ADDED TO Play CLASS '''
		
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


class Analyze_plays:
	'''
	This class stores and sorts objects of the Play class so that they can be efficiently accessed for processing.
	Overall list consisting of three separate lists each of which stores multiple instances of the Play class.
	'''

	def __init__(self,name=None):
		self.name = name
		self.first_down = [[],[],[],[],[],[],[],[],[],[]]
		self.second_down = [[],[],[],[],[],[],[],[],[],[]]
		self.third_down = [[],[],[],[],[],[],[],[],[],[]]
		self.fourth_down = []		
		self.plays_array = [self.first_down,self.second_down,self.third_down,self.fourth_down]
		self.number_plays = 0

	def __getnewargs__(self):
		return ()

	def __len__(self):
		return self.number_plays

	def add_play(self,play):
		self.number_plays += 1
		down = play.start_down
		if(down == None):
			return
		if(down != 4):
			try:
				to_go = play.distance_to_first
				self.plays_array[down-1][min(play.distance_to_first-1,9)].append(play)
			except AttributeError:
				a = 1
		else:
			self.plays_array[3].append(play)

	def retrieve_plays(self,down,yards):
		return self.plays_array[down-1][min(yards-1,9)]

	def reference_situation(self, situation):
		'''
		Should return tuple of 4 values (prob of run, pass short, pass medium, pass long)
		'''
		count = 0
		run_score = 0
		pass_short_score = 0
		pass_long_score = 0
		left_score = 0
		middle_score = 0
		right_score = 0
		for i in range(3):
			for j in range(10):
#				print(self.plays_array[i][j])
				for k in range(len(self.plays_array[i][j])):
					past_play = self.plays_array[i][j][k]
					offense = past_play.offense
					play_score = past_play.score_diff
					relevance_score = m.exp((-1.897*abs(situation.diff_score - play_score))/10)
					relevance_down = m.exp(-1.897*abs(situation.start_down - past_play.start_down))
					relevance_togo = m.exp(-1.897*abs(situation.distance_to_first-past_play.distance_to_first)/5)
					relevance_position = m.exp(-1.897*abs(situation.position - past_play.position)/35)
					if(situation.quarter != 1 and past_play.quarter != 1 and situation.quarter != 3 and past_play.quarter != 1):
						play_time_split = past_play.time.split(':')
						try:
							play_time = int(play_time_split[0])
						except ValueError:
							play_time = 0
						relevance_time = m.exp(-1.897*abs(situation.time - play_time)/5)
					else:
						relevance_time = 1
					total_relevance = relevance_score * relevance_down * relevance_togo * relevance_position * relevance_time
					count += 1
					if(past_play.play_type == 'rush'):
						run_score += total_relevance
					elif(past_play.play_type == 'pass'):
						if(past_play.passing_distance == 'Short'):
							pass_short_score += total_relevance
						else:
							pass_long_score += total_relevance
					if(past_play.direction == 'Right'):
						right_score += total_relevance
					elif(past_play.direction == 'Middle'):
						middle_score += total_relevance
					elif(past_play.direction == 'Left'):
						left_score += total_relevance
					count += 1

		# Normalization of Run, Pass Short, Pass Medium, Pass Long
		magnitude = run_score + pass_short_score + pass_long_score
		run_score = run_score / magnitude
		pass_short_score = pass_short_score / magnitude
		pass_long_score = pass_long_score / magnitude

		# Normalization of Left, Middle, Right
		magnitude_LMR = left_score + middle_score + right_score
		right_score = right_score / magnitude_LMR
		middle_score = middle_score / magnitude_LMR
		left_score = left_score / magnitude_LMR

		return (run_score, pass_short_score, pass_long_score, left_score, middle_score, right_score)

	def optimal_decision(self, situation):
		'''
		Should return 0 - Run, 1 - Short Pass, 2 - Long Pass
		'''
		# Finding expected returns for each option and associate standard deviation

		run_results = []
		short_pass_results = []
		long_pass_results = []
#		run_relevance = []
#		short_pass_relevance = []
#		long_pass_relevance = []

		count = 0
		relevance_cutoff = 0.85
		# Check each play in playbook

		for i in range(3):
			for j in range(10):
				for k in range(len(self.plays_array[i][j])):
					past_play = self.plays_array[i][j][k]
					offense = past_play.offense
					play_score = past_play.score_diff
					relevance_score = m.exp((-1.897*abs(situation.diff_score - play_score))/10)
					relevance_down = m.exp(-1.897*abs(situation.start_down - past_play.start_down))
					relevance_togo = m.exp(-1.897*abs(situation.distance_to_first-past_play.distance_to_first)/5)
					relevance_position = m.exp(-1.897*abs(situation.position - past_play.position)/35)
					if(situation.quarter != 1 and past_play.quarter != 1 and situation.quarter != 3 and past_play.quarter != 1):
						play_time_split = past_play.time.split(':')
						try:
							play_time = int(play_time_split[0])
						except ValueError:
							play_time = 0
						relevance_time = m.exp(-1.897*abs(situation.time - play_time)/5)
					else:
						relevance_time = 1
					total_relevance = relevance_score * relevance_down * relevance_togo * relevance_position * relevance_time
					if(total_relevance < relevance_cutoff):
						continue
					count += 1
					if(past_play.play_type == 'rush'):
						run_results.append(past_play.distance)
#						run_relevance.append(total_relevance)
					elif(past_play.play_type == 'pass'):
						if(past_play.passing_distance == 'Short'):
							short_pass_results.append(past_play.distance)
#							short_pass_relevance.append(total_relevance)
						else:
							long_pass_results.append(past_play.distance)
#							long_pass_relevance.append(total_relevance)

		# Run, Short Pass and Long Pass results and relevance recorded
		run_avg = np.median(run_results)
		run_std = np.std(run_results)
		short_avg = np.median(short_pass_results)
		short_std = np.std(short_pass_results)
		long_avg = np.median(long_pass_results)
		long_std = np.std(long_pass_results)

		# Three objective functions.
		# OBJ Func 1: Normal Game
		# f1 = avg - 0.8 * std
		# OBJ Func 2: Winning in last third of 4th quarter
		# f2 = avg - 1.2 * std
		# OBJ Func 3: Loosing in last third of 4th quarter
		# f3 = avg - 0.4 * std

		f_constants = [0.8,1.2,0.4]
		if(situation.quarter != 4 or situation.time > 5):
			f1 = np.array([None, None, None])
			f1[0] = run_avg - f_constants[0] * run_std
			f1[1] = short_avg - f_constants[0] * short_std
			f1[2] = long_avg - f_constants[0] * long_std
			if(f1[0] == max(f1)):
				return 0
			elif(f1[1] == max(f1)):
				return 1
			else:
				return 2
		elif(situation.diff_score >= 0):
			f2 = np.array([None, None, None])
			f2[0] = run_avg - f_constants[1] * run_std
			f2[1] = run_avg - f_constants[1] * run_std
			f2[2] = run_avg - f_constants[1] * run_std
			if(f2[0] == max(f1)):
				return 0
			elif(f2[1] == max(f1)):
				return 1
			else:
				return 2
		else:
			f3 = np.array([None, None, None])
			f3[0] = run_avg - f_constants[2] * run_std
			f3[1] = run_avg - f_constants[2] * run_std
			f3[2] = run_avg - f_constants[2] * run_std
			if(f3[0] == max(f1)):
				return 0
			elif(f3[1] == max(f1)):
				return 1
			else:
				return 2

class Situation:
	'''
	This class stores variables representing current game state.
	'''
	def __init__(self, start_down, distance_to_first, time, quarter, position, diff_score,team):
		self.start_down = start_down
		self.distance_to_first = distance_to_first
		self.time = time
		self.quarter = quarter
		self.position = position
		self.diff_score = diff_score
		self.team = team

def update(down,distance_to_first,time,quarter,position,diff_score,team):
	global play_hashtable
	situation = Situation(down,distance_to_first,time,quarter,position,diff_score,team)
	current_state = {}
	play_stats = play_hashtable[team].reference_situation(situation)
	current_state['Left'] = play_stats[5]
	current_state['Middle'] = play_stats[4]
	current_state['Right'] = play_stats[3]
	current_state['Rush'] = play_stats[0]
	current_state['Pass Short'] = play_stats[1]
	current_state['Pass Long'] = play_stats[2]

	decision = play_hashtable[team].optimal_decision(situation)
	if(decision == 0):
		current_state['Optimal'] = 'Rush'
	elif(decision == 1):
		current_state['Optimal'] = 'Pass Short'
	else:
		current_state['Optimal'] = 'Pass Long'
	return current_state