import pandas as pd
import numpy as np
import math

#The debug mode varaible
debug = True
#3 year MLB averages for: H/PA, BB/PA, K/PA, HR/H via FanGraphs
MLB_averages = [0.226, 0.084, 0.199, 0.138]

class player_stats:
    Hper = 0 #Hit percentage
    BBper = 1 #Walk percentaage
    Kper = 2 #Strikeout percentage
    HRper = 3 #Homerun percentage (of hits)

# Calculates the weight of the stats for a given game using an exponential method that
# weights more recent games higher than older games, maxing at the number of games as an input
def weight_calculator(game_number, max_games):
    return (((4**(1./max_games))**((game_number*-1.)+max_games))-1)

#Reads a .csv into a pandas dataframe, flips it vertically (so newer games are at the top)
def read_data(filepath):
    data = pd.read_csv(filepath).iloc[::-1]
    return data

#Returns a numpy array of fully adjusted statistics given the sample size (games), weighted based on recency. The format
#of the array is as follows:
#[H%, BB%, K%, HR%]
def calc_true_stats(data, pitcher_type):

    if(pitcher_type == 'S'):
        max_games = 50
    elif(pitcher_type == 'R'):
        max_games = 100
    else:
        print("Invalid pitcher type")
        return

    true_stats = np.zeros((4, 1))  #The final array to be returned
    true_stats_temp = np.zeros((4, 1)) #A placeholder array used for temporary data storage
    true_stats_PA = 0. #The number of weighted PA, used to divide the temp data storage by

    num_rows = len(data.index) #The number of rows in the dataframe

    max_index = min(max_games, num_rows) #The number of games, will max out at 500

    #Loop through the data and calculate the weighted raw statistics using the weight_calulator function
    for index, row in data.iterrows():
        if index <= max_games: #Only consider the most recent 50/100 games, depending on starter or reliever

            #Calculate the weight for this game so that we only have to do it once
            weight = weight_calculator(index, max_games)

            #Calculate the raw number for each stat
            true_stats_temp[player_stats.Hper] += row['H']*weight #Hits
            true_stats_temp[player_stats.BBper] += row['BB']*weight #Walks
            true_stats_temp[player_stats.Kper] += row['SO']*weight #Strikeouts
            true_stats_temp[player_stats.HRper] += row['HR']*weight #Homeruns

            #The weighted plate appearances
            true_stats_PA += row['TBF']*weight

    #Calculate their adjusted stats, unweighted for games at this point
    true_stats[player_stats.Hper] = true_stats_temp[player_stats.Hper]/true_stats_PA #BA, H/PA
    true_stats[player_stats.BBper] = true_stats_temp[player_stats.BBper]/true_stats_PA #BB%, BB/PA
    true_stats[player_stats.Kper] = true_stats_temp[player_stats.Kper]/true_stats_PA #K%, K/PA
    true_stats[player_stats.HRper] = true_stats_temp[player_stats.HRper]/true_stats_temp[player_stats.Hper] #HR%, HR/H

    #Check for NaN numbers, change to 0
    for i in range(0,3):
        if np.isnan(true_stats[i]):
            true_stats[i] = 0.

    #Prints out the unadjusted (for number of games) statistics if debug mode is on
    if debug == True:
        print("----------------")
        print("Unadjusted statistics")
        print("Games: ", max_index)
        print("uaH%: ", true_stats[0])
        print("uaBB%: ", true_stats[1])
        print("uaK%: ", true_stats[2])
        print("uaHR%: ", true_stats[3])
        print("----------------")
        print("")

    #Adjust for the number of games in the sample size
    for i in range(0,3):
        true_stats[i] = ((max_index/max_games)*true_stats[i])+((1-(max_index/max_games))*MLB_averages[i])

    #Prints out the adjusted (for number of games) statistics if debug mode is on
    if debug == True:
        print("----------------")
        print("Adjusted statistics")
        print("Games: ", max_index)
        print("aH%: ", true_stats[0])
        print("aBB%: ", true_stats[1])
        print("aK%: ", true_stats[2])
        print("aHR%: ", true_stats[3])
        print("----------------")
        print("")

    return true_stats

test_stats = read_data("Data/JamesPaxtonGameLog.csv")
calc_true_stats(test_stats, 'S')