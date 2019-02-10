import pandas as pd
import numpy as np

#The league averages in 2018 for [AVG, OBP, SLG, BB%, K%]
league_average = [0.248, 0.318, 0.409, 0.085, 0.223]

#The odds ratio method
def odds_ratio(batter_stat, pitcher_stat, league_average):
	odds_b = batter_stat/(1-batter_stat)
	odds_p = pitcher_stat/(1-pitcher_stat)
	odds_l = league_average/(1-league_average)
	odds = (odds_b*odds_p)/odds_l
	return odds/(odds+1)

#The bater pitcher matchup regression
def batter_pitcher_matchup(input_data):

	#The pitcher stats are stored in Lineups/Pitcher.csv
	pitcher_stats = np.genfromtxt('Lineups/Pitcher.csv', delimiter=",")

	output_data = pd.DataFrame()

	output_data['Name'] = input_data['Name']

	output_data['AVG'] = odds_ratio(input_data['AVG'], pitcher_stats[1], league_average[0]) \
	 + (pitcher_stats[2]*0.164 + input_data['OBP']*0.08 + pitcher_stats[4]*0.188 \
	 	+ input_data['BB%']*0.159 + ((pitcher_stats[4]-input_data['BB%'])**2)*-0.4 - 0.076)

	output_data['OBP'] = odds_ratio(input_data['OBP'], pitcher_stats[2], league_average[1]) \
	 + (input_data['BB%']*0.126 + pitcher_stats[5]*0.109 + pitcher_stats[2]*0.092 + pitcher_stats[3]*0.058 \
	 	+ pitcher_stats[1]*-0.103 - 0.085)
	
	output_data['SLG'] = odds_ratio(input_data['SLG'], pitcher_stats[3], league_average[2]) \
	 + (pitcher_stats[4]*-0.509 + input_data['BB%']*-0.521 + pitcher_stats[3]*0.162 + input_data['SLG']*0.066 \
	 	+ pitcher_stats[5]*0.122 - 0.113)

	"""
	output_data['BB%'] = odds_ratio(input_data['BB%'], pitcher_stats[4], league_average[3]) \
	 + (input_data['BB%']*0.107 + pitcher_stats[4]*-0.521 + ((pitcher_stats[1]-input_data['AVG'])**2)*0.338 + ((pitcher_stats[2]-input_data['OBP'])**2)*-0.2 \
	 	+ input_data['SLG']*0.018 - 0.018)
	"""

	output_data['BB%'] = output_data['OBP'] - output_data['AVG']

	#There is no adjustment for K% besides the odds ratio method
	output_data['K%'] = odds_ratio(input_data['K%'], pitcher_stats[5], league_average[4])

	#Players with an abnormally low BB% (pitchers, especially) can end up with a negative
	#value when facing good pitchers. This sets all negative values to 0
	output_data['BB%'] = output_data['BB%'].clip_lower(0.00)

	return output_data


#Alters the batting tiers for the given pitcher using odds ratio method
def batting_tiers_pitchers_matchup(averages, stat):

	pitcher_stats = np.genfromtxt('Lineups/Pitcher.csv', delimiter=",")

	if stat == 'AVG':
		pos = 0
	if stat == 'OBP':
		pos = 1
	if stat == 'SLG':
		pos = 2
	if stat == 'BB%':
		pos = 3
	if stat == 'K%':
		pos = 4

	for i in range(0, len(averages)):
		averages[i] = odds_ratio(averages[i], pitcher_stats[pos+1], league_average[pos])

	return averages



