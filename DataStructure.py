class List_plays:
	'''
	This class stores and sorts objects of the Play class so that they can be efficiently accessed for processing.
	Overall list consisting of three separate lists each of which stores multiple instances of the Play class.
	'''

	def __init__(self):
		self.first_down = [[],[],[],[],[],[],[],[],[],[]]
		self.second_down = [[],[],[],[],[],[],[],[],[],[]]
		self.third_down = [[],[],[],[],[],[],[],[],[],[]]
		self.plays_array = [self.first_down,self.second_down,self.third_down]
		self.number_plays = 0

	def __getnewargs__(self):
		return ()

	def add_play(self,play):
		down = play.start_down
		to_go = play.distance_to_first
		self.plays_array[down-1][min(play.distance_to_first-1,9)].append(play)

	def retrieve_plays(self,down,yards):
		return self.plays_array[down-1][min(yards-1,9)]

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

	def __init__(self,offense,defense,start_down,distance_to_first,end_down,end_distance_to_first,play_type,play_type_detail,turnover,position,score_offense,score_defense,time,quarter,player):
		self.offense = offense
		self.defense = defense
		self.start_down = start_down
		self.distance_to_first = distance_to_first
		self.end_down = end_down
		self.end_distance_to_first = end_distance_to_first
		self.play_type = play_type
		self.play_type_detail = play_type_detail
		self.turnover = turnover
		self.position = position
		self.score_offense = score_offense
		self.score_defense = score_defense
		self.time = time
		self.quarter = quarter
		self.player = player

	def __lt__(self,other):
		return self.distance_to_first <= other.distance_to_first

	def __str__(self):
		string = 'Offense:'
		string += self.offense
		string += ' Defense:'
		string += self.defense
		string += ' Down:'
		string += str(self.start_down)
		string += ' To go:'
		string += str(self.distance_to_first)
		string += ' Play:'
		if(self.play_type == 0):
			string += 'Run '
			if(self.play_type_detail == 0):
				string += 'Left'
			elif(self.play_type_detail == 1):
				string += 'Middle'
			else:
				string += 'Right'
		else:
			string += 'Pass '
			if(self.play_type_detail == 0):
				string += 'Short'
			elif(self.play_type_detail == 1):
				string += 'Medium'
			else:
				string += 'Long'
		return string
