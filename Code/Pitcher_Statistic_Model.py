import pandas as pd
import numpy as np
import math
import os

#The debug mode varaible
debug = True
#Testing mode, used to test the weight function
test_mode = True

#The MLB averages for 2018 the correspond to the second part of class pitcher (8-12)
#BA, OBP, HR% (HR/ABs), K%, BB%
pitcher_averages = [0.248, 0.318, 0.034, 0.223, 0.085]

#This class is used to keep track of the data in the arrays
class pitcher:

    #The following are used directly for OOTP ratings
    BF = 0 #Batters faced
    AB = 1 #At-bats
    IP = 2 #Innings Pitched
    HA = 3 #Hits allowed
    HRA = 4 #Homeruns allowed
    BB = 5 #Base on balls
    HP = 6 #Hit batters
    K = 7 #Strikeouts

    #The following are used for batter-pitcher matchups
    BA = 8 #Batting average against
    OBP = 9 #On base percentage against
    HRper = 10 #Homerun percentage
    Kper = 11 #Strikeout percentage
    BBper = 12 #Base on balls percentage
    
# Calculates the weight of the stats for a given game using an exponential method that
# weights more recent games higher than older games, maxing at the number of games as an input
def weight_calculator(game_number, max_games):
    return (((4**(1./max_games))**((game_number*-1.)+max_games))-1)

#Reads a .csv into a pandas dataframe, delete the "Totals" row, sort so newest first, reindex
def read_data(filepath):
    data = pd.read_csv(filepath)
    data = data[~data['Date'].astype(str).str.startswith('T')]
    data = data.sort_values(by='Date', ascending=False)
    data = data.reset_index(drop=True)
    return data

#Used for debug reasons to print the stat arrays
def print_array(array, title):
    print ("\n")
    print("###############")
    print(title, "\n")
    print("BF: ", array[pitcher.BF])
    print("AB: ", array[pitcher.AB])
    print("IP: ", array[pitcher.IP])
    print("HA: ", array[pitcher.HA])
    print("HRA: ", array[pitcher.HRA])
    print("BB: ", array[pitcher.BB])
    print("HP: ", array[pitcher.HP])
    print("K: ", array[pitcher.K])
    print("--------------")
    print("BA: ", array[pitcher.BA])
    print("OBP: ", array[pitcher.OBP])
    print("HR%: ", array[pitcher.HRper])
    print("K%: ", array[pitcher.Kper])
    print("BB%: ", array[pitcher.BBper])
    print("###############")
    print ("\n")
        

def calc_stats(data):

    max_games = 50

    stats = np.zeros((13, 1))  #The final array to be returned
    num_rows = len(data.index) #The number of rows in the dataframe

    max_index = min(max_games, num_rows) #The number of games, will max out at 50

    #If test_mode (for testing the weighting function) is on, run it on the most recent three games (two weeks)
    if test_mode == True:
        recent_stats = np.zeros((13,1))

        #Loop through the data and calculate the weighted raw statistics using the weight_calulator function for the most recent 3 games
        for index, row in data.iterrows():
            if index < 3: #Only consider the most recent 3 games to compare the rest of the data to

                #Calculate the raw stats for the last 5 games
                recent_stats[pitcher.BF] += row['TBF']
                recent_stats[pitcher.IP] += row['IP']
                recent_stats[pitcher.HA] += row['H']
                recent_stats[pitcher.HRA] += row['HR']
                recent_stats[pitcher.BB] += row['BB']
                recent_stats[pitcher.HP] += row['HBP']
                recent_stats[pitcher.K] += row['SO']

        #Calculate the rest of the stats 
        recent_stats[pitcher.AB] = recent_stats[pitcher.BF] - (recent_stats[pitcher.BB] + recent_stats[pitcher.HP])
        recent_stats[pitcher.BA] = recent_stats[pitcher.HA]/recent_stats[pitcher.AB]
        recent_stats[pitcher.OBP] = (recent_stats[pitcher.HA]+recent_stats[pitcher.BB]+recent_stats[pitcher.HP])/recent_stats[pitcher.BF]
        recent_stats[pitcher.HRper] = recent_stats[pitcher.HRA]/recent_stats[pitcher.AB]
        recent_stats[pitcher.Kper] = recent_stats[pitcher.K]/recent_stats[pitcher.BF]
        recent_stats[pitcher.BBper] = recent_stats[pitcher.BB]/recent_stats[pitcher.BF]

        if debug == True:
            print_array(recent_stats, "Most Recent 3 Games")

        #Delete the most recent 5 games, reset the index, recalculate the size statistics
        data = data.iloc[3:]
        data = data.reset_index(drop=True)
        num_rows = len(data.index) #The number of rows in the dataframe, reinstanced after the change in size
        max_index = min(max_games, num_rows) #The number of games, will max out at 50, reinstanced after the change in size

    #Loop through the data and calculate the weighted statistics using the weight_calulator function
    for index, row in data.iterrows():
        if index < max_index: #Only consider the most recent 5 games to compare the rest of the data to

            weight = weight_calculator(index, max_games)

            #Calculate the raw stats for the last 50 games or less (if not enough data)
            recent_stats[pitcher.BF] += row['TBF']*weight
            recent_stats[pitcher.IP] += row['IP']*weight
            recent_stats[pitcher.HA] += row['H']*weight
            recent_stats[pitcher.HRA] += row['HR']*weight
            recent_stats[pitcher.BB] += row['BB']*weight
            recent_stats[pitcher.HP] += row['HBP']*weight
            recent_stats[pitcher.K] += row['SO']*weight

    recent_stats[pitcher.AB] = recent_stats[pitcher.BF] - (recent_stats[pitcher.BB] + recent_stats[pitcher.HP])
    recent_stats[pitcher.BA] = recent_stats[pitcher.HA]/recent_stats[pitcher.AB]
    recent_stats[pitcher.OBP] = (recent_stats[pitcher.HA]+recent_stats[pitcher.BB]+recent_stats[pitcher.HP])/recent_stats[pitcher.BF]
    recent_stats[pitcher.HRper] = recent_stats[pitcher.HRA]/recent_stats[pitcher.AB]
    recent_stats[pitcher.Kper] = recent_stats[pitcher.K]/recent_stats[pitcher.BF]
    recent_stats[pitcher.BBper] = recent_stats[pitcher.BB]/recent_stats[pitcher.BF]

    #Adjust for the number of games in the sample size
    for i in range(0,5):
        stats[i] = ((max_index/max_games)*stats[i+8])+((1-(max_index/max_games))*pitcher_averages[i])

    if debug == True:
        print_array(recent_stats, "Overall Stats")

#Run the program on a given file
def run(filename):
    print("Running on", filename)
    calc_stats(read_data(filename))

#Loop through all of the pitcher files in the \Data\Pitchers dir
def main():
    for root, dirs, files in os.walk(os.getcwd()+'\Data\Pitchers'):
       for fname in files:
           run('Data\Pitchers\\' + fname)

main()