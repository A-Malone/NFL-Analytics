from Classes import Play, Analyze_plays, Situation
import pickle

plays_file = open('sample_plays','rb')
play_hashtable = pickle.load(plays_file)

start_down = 1
distance_to_first = 10
time = 15
quarter = 1
position = 80
diff_score = 0 # Offense score - Defense Score
team = 'NE'

playbook = Analyze_plays('playbook')
'''
for i in range(60):
	try:
		print(plays_array[i].sequence, plays_array[i].play_type, plays_array[i].passing_distance)
	except AttributeError:
		continue
'''
#for key in play_hashtable:
#	number_plays = len(play_hashtable[key])
#	print(key)
#	print(play_hashtable[key])

'''
for i in range(number_plays - 1):
#	print(i)
	playbook.add_play(plays_array[i])
'''

current_situation = Situation(start_down,distance_to_first,time,quarter,position,diff_score,team)
'''
scores = []
for i in range(19):
	position = 5 + 5*i
#	print(position)
	scores.append(play_hashtable[team].reference_situation(Situation(start_down,distance_to_first,time,quarter,position,diff_score,team)))

output = open('NE_play_breakdown.csv','w')
for entry in scores:
	for part in entry:
		output.write(str(part))
		output.write(',')
	output.write('\n')
'''
scores = play_hashtable[team].reference_situation(current_situation)

print('Run:',scores[0],' Pass Short:',scores[1],' Pass Long:',scores[2])
print('Right:',scores[3],' Middle:',scores[4],' Left:',scores[5])

optimal = play_hashtable[team].optimal_decision(current_situation)
print(optimal)