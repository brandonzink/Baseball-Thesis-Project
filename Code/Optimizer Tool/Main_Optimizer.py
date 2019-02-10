import pandas as pd
import numpy as np
import sys

test = True #If in testing mode
ranking_method = 'Team' #The ranking method, either Team or MLB for stat rankings

#Hold the batting stat/position results from the simulations
normalized_results_al = np.zeros((45, 5))
normalized_results_nl = np.zeros((45, 5))

#Fills the normalized results arrays as defined above
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


#Gets the weight for the given spot based on the input
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

	#The order of importance of the position in the batting order fr each league
	#Ex. the fifth spot is the most important in the AL
	al_pos_ranks = [5, 3, 2, 1, 6, 7, 4, 8, 9]
	nl_pos_ranks = [1, 4, 2, 3, 5, 6, 8, 9, 7]

	final_lineup = []

	lineup = pd.read_csv(filename)

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

		if ranking_method == 'MLB':
			print("Error: MLB rankings method not implemented")
			return


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

	#While we have not assigned a player to each batting order spot
	while not lineup.empty:

		#Get the position of the max in each column of the array
		max_pos_array = np.argmax(scores, axis=0)
		print(max_pos_array)

		#Get the max pos for the spot in the order we are looking for
		max_pos = max_pos_array[rankings[0]-1]
		print(max_pos)

		if test == True:
			print("Spot:", rankings[0], ", Player:", lineup.iloc[max_pos]['Name'])

		final_lineup.append((rankings[0],". ", lineup.iloc[max_pos]['Name']))

		lineup = lineup[lineup['Name'] != lineup.iloc[max_pos]['Name']]
		rankings.pop(0)

	def sort_by_batting_pos(element):
		return element[0]

	final_lineup.sort(key=sort_by_batting_pos)

	for player in final_lineup:
		print(player[0],".", player[2])
















fill_normalized_results()
score_lineup(sys.argv[1], sys.argv[2])
