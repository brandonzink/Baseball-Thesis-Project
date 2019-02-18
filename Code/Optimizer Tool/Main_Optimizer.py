import pandas as pd
import numpy as np
import sys
import Stat_Prediction_Applied
import Batter_Pitcher_Matchup_Applied
import re

test = False #If in testing mode, prints more stuff

"""
The players can either be ranked based on where they rank as compared to their
teammates (in tiers of 1-2-3-2-1), or based on where they rank in the MLB as a whole
(in tiers of 30-60-90-60-30). The cutoffs for the simulations were based on the MLB
cutoffs, both will be tested to see which is more accurate. 
"""
ranking_method = 'MLB' #Either Team or MLB for stat rankings

selection_order_method = 'Optimal' #Either ordered or optimal, if optimal, weights by the relative run production

#Hold the batting stat/position results from the simulations
normalized_results_al = np.zeros((45, 5))
normalized_results_nl = np.zeros((45, 5))

#Holds the optimal lineup since it was easier than trying to pass it through recursion a bunch
global_lineup = []


#Brute forces an optimal lineup
def lineup_selector_brute_force(scores, lineup):

	global_max_score = 0

	lineup_spot_left = [1, 2, 3, 4, 5, 6, 7, 8, 9]

	def lineup_recurive(scores, lineup, final_lineup, lineup_score, lineup_spot_left):

		nonlocal global_max_score
		global global_lineup


		#If the lineup is complete, check to see if it is the best so far, if so, print
		if lineup.empty:
			if lineup_score > global_max_score:
				global_max_score = lineup_score
				global_lineup = final_lineup

				"""
				#Print the opposing pitchers and best lineup
				print("---------------")
				print("New Best Lineup")
				#Sorts it based on the batting position order
				def sort_by_batting_pos(element):
					return element[0]
				final_lineup.sort(key=sort_by_batting_pos)

				#Get the opposing SP
				print("Opposing SP:",re.sub(r'[^a-zA-Z ]', "",np.genfromtxt('Lineups/Pitcher.csv', delimiter=",", dtype=str)[0]))

				#Prints the lineup
				for player in final_lineup:
					print(str(player[0])+".", player[1],"-", str(round(player[2],3))+"/"+str(round(player[3],3))+"/"+str(round(player[4],3)),str(round(player[5],1))+"%", str(round(player[6],1))+"%")
				"""
		#If the lineup is not empty, loop through the options
		if lineup.empty == False:
			for i in range(0, scores.shape[0]):
				if i < len(lineup_spot_left):

					#Record the scores for the current lineup, and pass it on recursively
					lineup_score += scores[0][i] #Add the current position to the score
					final_lineup.append((lineup_spot_left[i], lineup.iloc[0]['Name'], lineup.iloc[0]['AVG'], lineup.iloc[0]['OBP'], lineup.iloc[0]['SLG'], (lineup.iloc[0]['BB%']*100), (lineup.iloc[0]['K%']*100)))
					lineup_spot_left.pop(i) #Remoce the current position from the lineup
					lineup = lineup[lineup['Name'] != lineup.iloc[0]['Name']]
					scores = np.delete(scores, 0, 0)
					scores = np.delete(scores, i, 1)

					lineup_recurive(scores.copy(), lineup.copy(), final_lineup.copy(), lineup_score, lineup_spot_left.copy())


	lineup_recurive(scores.copy(), lineup.copy(), [], 0, lineup_spot_left.copy())
	return


#Fills the normalized results arrays as defined above from the simulations
def fill_normalized_results():

	global normalized_results_al
	global normalized_results_nl

	normalized_results_al = np.genfromtxt('Data/Normalized_Results_AL.txt')
	normalized_results_nl = np.genfromtxt('Data/Normalized_Results_NL.txt')

	if test == True:
		print("AL Results")
		print(normalized_results_al)
		print("-----")
		print("NL Results")
		print(normalized_results_nl)


#Gets the weight for the given stat, league, and position in the batting
#order. Will return a value between 0 and 100 inclusive.
def get_weight(league, spot, rank, stat):

	def get_stat(stat):
		if stat == 'AVG':
			return 0
		if stat == 'OBP':
			return 1
		if stat == 'SLG':
			return 2
		if stat == 'BB%':
			return 3
		if stat == 'K%':
			return 4

	def get_rank(rank):
		if rank == 'High':
			return 0
		if rank == 'Med High':
			return 1
		if rank == 'Normal':
			return 2
		if rank == 'Med Low':
			return 3
		if rank == 'Low':
			return 4

	if league == 'NL':
		return normalized_results_nl[((spot-1)*5)+get_rank(rank)][get_stat(stat)]

	if league == 'AL':
		return normalized_results_al[((spot-1)*5)+get_rank(rank)][get_stat(stat)]


#Does the actual scoring of the lineup
def score_lineup(filename, league):

	#The order of importance of the position in the batting order for each league
	#as found via the 'Mike Trout' simulation
	#Ex. the fifth spot is the most important in the AL
	al_pos_ranks = [5, 3, 2, 1, 6, 7, 4, 8, 9]
	nl_pos_ranks = [1, 4, 2, 3, 5, 6, 8, 7, 9]

	#Holds the final optimized lineup to be printed from
	final_lineup = []

	#Applies the stat prediction equations from the writeup
	lineup = Stat_Prediction_Applied.predictive_data(filename)
	if test == True:
		print("Post Stat_Prediction_Applied, Pre Batter_Pitcher_Matchup_Applied")
		print(lineup)

	#Applies the batter pitcher matchup equations from the writeup
	lineup = Batter_Pitcher_Matchup_Applied.batter_pitcher_matchup(lineup)
	if test == True:
		print("Post Batter_Pitcher_Matchup_Applied")
		print(lineup)


	#Creats ranks columns in the dataframe
	lineup['AVG_Rank'] = 10-lineup['AVG'].rank()
	lineup['OBP_Rank'] = 10-lineup['OBP'].rank()
	lineup['SLG_Rank'] = 10-lineup['SLG'].rank()
	lineup['BB%_Rank'] = 10-lineup['BB%'].rank()
	lineup['K%_Rank'] = lineup['K%'].rank()

	if test == True:
		print("Running with", filename)
		print(lineup)

	#Holds the score for each position
	scores = np.zeros((9, 9))

	#Returns the string version of the rank
	def get_rank_string(rank, stat, value, league):
		if ranking_method == 'Team':
			if rank == 1:
				return 'High'
			if rank == 2 or rank == 3:
				return 'Med High'
			if rank > 3 and rank < 7:
				return 'Normal'
			if rank == 7 or rank == 8:
				return 'Med Low'
			if rank == 9:
				return 'Low'

		#Returns the rank based on where they rank within the MLB
		if ranking_method == 'MLB':
			AVG_cutoffs = Batter_Pitcher_Matchup_Applied.batting_tiers_pitchers_matchup([.296, .272, .251, .238], 'AVG')
			OBP_cutoffs = Batter_Pitcher_Matchup_Applied.batting_tiers_pitchers_matchup([.374, .345, .322, .307], 'OBP')
			SLG_cutoffs = Batter_Pitcher_Matchup_Applied.batting_tiers_pitchers_matchup([.512, .460, .414, .384], 'SLG')
			BB_cutoffs = Batter_Pitcher_Matchup_Applied.batting_tiers_pitchers_matchup([0.134, 0.105, 0.084, 0.071], 'BB%')
			K_cutoffs = Batter_Pitcher_Matchup_Applied.batting_tiers_pitchers_matchup([0.189, 0.216, 0.253, 0.304], 'K%')

			if stat == 'AVG':
				cutoffs = AVG_cutoffs
			if stat == 'OBP':
				cutoffs = OBP_cutoffs
			if stat == 'SLG':
				cutoffs = SLG_cutoffs
			if stat == 'BB%':
				cutoffs = BB_cutoffs
			if stat == 'K%':
				cutoffs = K_cutoffs

			#Finds the rank and returns the i value used to look up the string version
			def return_i(cutoffs, stat, value):
				for i in range(0,4):
					if stat != 'K%':
						if value >= cutoffs[i]:
							return i
					else:
						if value <= cutoffs[i]:
							return i
				return 4

			i_rank = return_i(cutoffs, stat, value)

			if i_rank == 0:
				return 'High'
			if i_rank == 1:
				return 'Med High'
			if i_rank == 2:
				return 'Normal'
			if i_rank == 3:
				return 'Med Low'
			if i_rank == 4:
				return 'Low'


	#Get the weights for each player/position combo
	for index, row in lineup.iterrows():
		for batting_pos in range(0, 9):
			AVG_score = get_weight(league, int(batting_pos), get_rank_string(row['AVG_Rank'], 'AVG', row['AVG'], league), 'AVG')
			OBP_score = get_weight(league, int(batting_pos), get_rank_string(row['OBP_Rank'], 'OBP', row['OBP'], league), 'OBP')
			SLG_score = get_weight(league, int(batting_pos), get_rank_string(row['SLG_Rank'], 'SLG', row['SLG'], league), 'SLG')
			BB_score = get_weight(league, int(batting_pos), get_rank_string(row['BB%_Rank'], 'BB%', row['BB%'], league), 'BB%')
			K_score = get_weight(league, int(batting_pos), get_rank_string(row['K%_Rank'], 'K%', row['K%'], league), 'K%')
			scores[index][batting_pos] = AVG_score + OBP_score + SLG_score + BB_score + K_score

	if test == True:
		print("Score Matrix")
		print(scores)

	if league == 'AL':
		rankings = al_pos_ranks.copy()
	if league == 'NL':
		rankings = nl_pos_ranks.copy()

	if selection_order_method == 'Optimal':

		#The relative run gain for each position in the batting order as determined by the simulations
		if league == 'AL':
			relative_runs = [1.033, 1.034, 1.037, 1.024, 1.038, 1.028, 1.025, 1.015, 1]
		if league == 'NL':
			relative_runs = [1.017, 1.014, 1.009, 1.016, 1.006, 1.004, 1.001, 1.002, 1]

		#Updates the score matrix multiplied by the relative runs at that position
		for row in range(0, scores.shape[0]):
			for col in range(0, scores.shape[1]):
				scores[row][col] = scores[row][col]*relative_runs[col]

		if test == True:
			print("Adjusted Score Matrix")
			print(scores)


		final_lineup = lineup_selector_brute_force(scores, lineup)

	#While we have not assigned a player to each batting order spot
	while not lineup.empty and selection_order_method == 'Ordered':

		#Get the position of the max in each column of the array
		max_pos_array = np.argmax(scores, axis=0)

		if test == True:
			print(max_pos_array)

		#Get the max pos for the spot in the order we are looking for
		max_pos = max_pos_array[rankings[0]-1]
		if test == True:
			print(max_pos)

		if test == True:
			print("Spot:", rankings[0], ", Player:", lineup.iloc[max_pos]['Name'])

		final_lineup.append((rankings[0], lineup.iloc[max_pos]['Name'], lineup.iloc[max_pos]['AVG'], lineup.iloc[max_pos]['OBP'], lineup.iloc[max_pos]['SLG'], (lineup.iloc[max_pos]['BB%']*100), (lineup.iloc[max_pos]['K%']*100)))

		lineup = lineup[lineup['Name'] != lineup.iloc[max_pos]['Name']]
		rankings.pop(0)
		scores = np.delete(scores, max_pos, 0)






	"""
	This seciton of code prints the lineup
	"""
	print("---------------------------------------------------")
	if selection_order_method == 'Optimal':
		final_lineup = global_lineup
	#Sorts it based on the batting position order
	def sort_by_batting_pos(element):
		return element[0]
	final_lineup.sort(key=sort_by_batting_pos)

	#Get the opposing SP
	print("[Opposing SP:",str(re.sub(r'[^a-zA-Z ]', "",np.genfromtxt('Lineups/Pitcher.csv', delimiter=",", dtype=str)[0]))+']')



	print("%-2s %-20.20s %17s %5s %5s" % ("", "Name", "AVG / OBP / SLG", "BB%", "K%"))
	#Prints the lineup
	for player in final_lineup:
		#print(str(player[0])+".", player[1],"-", str(round(player[2],3))+"/"+str(round(player[3],3))+"/"+str(round(player[4],3)),str(round(player[5],1))+"%", str(round(player[6],1))+"%")
		print("%-2s %-20.20s %17s %5s %5s" % (str(player[0])+".", str(player[1]), str(format(player[2],'.3f'))+"/"+str(format(player[3],'.3f'))+"/"+str(format(player[4],'.3f')), str(format(player[5],'.1f'))+"%", str(format(player[6],'.1f'))+"%"))
	print("---------------------------------------------------")

#Runs the functions
fill_normalized_results()
score_lineup(sys.argv[1], sys.argv[2])
