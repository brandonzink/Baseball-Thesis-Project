import pandas as pd
import numpy as np
import math
import os

#The debug mode varaible
debug = False
#Testing mode, used to test the weight function
test_mode = True

#The number of games back to test the model against
games_back = 40

#Correlation matrix, used if test_mode = true to test the correlation of a games back model
corr_matrix = np.zeros((12, 1))

#The MLB averages for 2018 the correspond to the second part of class batter (8-12)
#BA, OBP, SLG, HR% (HR/ABs), K%, BB%
pitcher_averages = [0.248, 0.318, 0.409, 0.034, 0.223, 0.085]

#This class is used to keep track of the data in the arrays
class batter:

    #The following are used to calculate other ratings
    PA = 0 #Plate appearances
    AB = 1 #At-bats
    H = 2 #Hits
    DB_H = 3 #Doubles
    TR_H = 4 #Triples
    HR = 5 #Homeruns
    BB = 6 #Base on balls
    K = 7 #Strikeouts

    #The following are used for batter-pitcher matchups
    BA = 8 #Batting average against
    OBP = 9 #On base percentage against
    SLG = 10 #Slugging
    HRper = 11 #Homerun percentage
    Kper = 12 #Strikeout percentage
    BBper = 13 #Base on balls percentage
    
# Calculates the weight of the stats for a given game using an exponential method that
# weights more recent games higher than older games, maxing at the number of games as an input
def weight_calculator(game_number, max_games):
    return (((3.513**(1./max_games))**((game_number*-1.)+max_games))-1)

#Reads a .csv into a pandas dataframe, delete the "Totals" row, drop the % on the BB% and K% columns, sort so newest first, reindex
def read_data(filepath):
    data = pd.read_csv(filepath)
    data = data[~data['Date'].astype(str).str.startswith('T')]
    data['BB%'] = (data['BB%'].str.strip('%').astype(float))*0.01
    data['K%'] = (data['K%'].str.strip('%').astype(float))*0.01
    data = data.sort_values(by='Date', ascending=False)
    data = data.reset_index(drop=True)
    return data

#Used for debug reasons to print the stat arrays
def print_array(array, title):
    print("###############")
    print(title, "\n")
    print("PA: ", array[batter.PA])
    print("AB: ", array[batter.AB])
    print("H: ", array[batter.H])
    print("2B: ", array[batter.DB_H])
    print("3B: ", array[batter.TR_H])
    print("HR: ", array[batter.HR])
    print("BB: ", array[batter.BB])
    print("K: ", array[batter.K])
    print("--------------")
    print("BA: ", array[batter.BA])
    print("OBP: ", array[batter.OBP])
    print("SLG: ", array[batter.SLG])
    print("HR%: ", array[batter.HRper])
    print("K%: ", array[batter.Kper])
    print("BB%: ", array[batter.BBper])
    print("###############")
    print ("\n")
        

def calc_stats(data):

    max_games = games_back

    stats = np.zeros((14, 1))  #The final array to be returned
    num_rows = len(data.index) #The number of rows in the dataframe

    max_index = min(max_games, num_rows) #The number of games, will max out at 50

    #If test_mode (for testing the weighting function) is on, run it on the most recent three games (two weeks)
    if test_mode == True:
        recent_stats = np.zeros((14,1))

        #Loop through the data and calculate the weighted raw statistics for the most recent 10 games
        for index, row in data.head(10).iterrows():
            if index < 10: #Only consider the most recent 10 games to compare the rest of the data to

                #Calculate the raw stats for the last 10 games
                recent_stats[batter.PA] += row['PA']
                recent_stats[batter.H] += row['H']
                recent_stats[batter.DB_H] += row['2B']
                recent_stats[batter.TR_H] += row['3B']
                recent_stats[batter.HR] += row['HR']
                recent_stats[batter.BB] += row['BB%']*row['PA']
                recent_stats[batter.K] += row['K%']*row['PA']

        #Calculate the rest of the stats 
        recent_stats[batter.AB] = recent_stats[batter.PA] - (recent_stats[batter.BB])
        recent_stats[batter.BA] = recent_stats[batter.H]/recent_stats[batter.AB]
        recent_stats[batter.OBP] = (recent_stats[batter.H]+recent_stats[batter.BB])/recent_stats[batter.PA]
        recent_stats[batter.SLG] = ((recent_stats[batter.HR]*4)+(recent_stats[batter.TR_H]*3)+(recent_stats[batter.DB_H]*2)+(recent_stats[batter.H]-recent_stats[batter.HR]-recent_stats[batter.TR_H]-recent_stats[batter.DB_H]))/recent_stats[batter.AB]
        recent_stats[batter.HRper] = recent_stats[batter.HR]/recent_stats[batter.AB]
        recent_stats[batter.Kper] = recent_stats[batter.K]/recent_stats[batter.PA]
        recent_stats[batter.BBper] = recent_stats[batter.BB]/recent_stats[batter.PA]

        if debug == True:
            print_array(recent_stats, "Most Recent 3 Games")

        #Delete the most recent 10 games, reset the index, recalculate the size statistics
        data = data.iloc[10:]
        data = data.reset_index(drop=True)
        num_rows = len(data.index) #The number of rows in the dataframe, reinstanced after the change in size
        max_index = min(max_games, num_rows) #The number of games, will max out at 50, reinstanced after the change in size

    #Loop through the data and calculate the weighted statistics using the weight_calulator function
    for index, row in data.head(games_back).iterrows():

        #Used to calculate the unweighted AB
        unweighted_BB = 0

        if index < max_index: 

            weight = weight_calculator(index, max_games)

            #Calculate the raw stats for the last games_back games or less (if not enough data)
            stats[batter.PA] += row['PA']
            stats[batter.H] += row['H']*weight
            stats[batter.DB_H] += row['2B']*weight
            stats[batter.TR_H] += row['3B']*weight
            stats[batter.HR] += row['HR']*weight
            stats[batter.BB] += row['BB%']*row['PA']*weight
            unweighted_BB += row['BB%']*row['PA']
            stats[batter.K] += row['K%']*row['PA']*weight

        stats[batter.AB] = stats[batter.PA]-unweighted_BB
        stats[batter.BA] = stats[batter.H]/stats[batter.AB]
        stats[batter.OBP] = (stats[batter.H]+stats[batter.BB])/stats[batter.PA]
        stats[batter.HRper] = stats[batter.HR]/stats[batter.AB]
        stats[batter.SLG] = ((stats[batter.HR]*4)+(stats[batter.TR_H]*3)+(stats[batter.DB_H]*2)+(stats[batter.H]-stats[batter.HR]-stats[batter.TR_H]-stats[batter.DB_H]))/stats[batter.AB]
        stats[batter.Kper] = stats[batter.K]/stats[batter.PA]
        stats[batter.BBper] = stats[batter.BB]/stats[batter.PA]

    #Adjust for the number of games in the sample size
    for i in range(0,6):
        stats[i+8] = ((max_index/max_games)*stats[i+8])+((1-(max_index/max_games))*pitcher_averages[i])

    if debug == True:
        print_array(stats, "Overall Stats")

    if test_mode == True:

        global corr_matrix

        temp_array = np.zeros((12, 1))

        #Overll stats
        temp_array[0][0] = stats[8]
        temp_array[1][0] = stats[9]
        temp_array[2][0] = stats[10]
        temp_array[3][0] = stats[11]
        temp_array[4][0] = stats[12]
        temp_array[5][0] = stats[13]

        #Two week stats
        temp_array[6][0] = recent_stats[8]
        temp_array[7][0] = recent_stats[9]
        temp_array[8][0] = recent_stats[10]
        temp_array[9][0] = recent_stats[11]
        temp_array[10][0] = recent_stats[12]
        temp_array[11][0] = recent_stats[13]

        corr_matrix = np.concatenate((corr_matrix, temp_array), axis=1)

#Run the program on a given file
def run(filename):
    print("Running on", filename)
    calc_stats(read_data(filename))

#Test the correlation of the corresponding varaibles given the number of games back
def correlation_test(matrix):

    #Calculate the coefficents
    BA_coef = np.corrcoef(matrix[0], matrix[6])[0,1]
    OBP_coef = np.corrcoef(matrix[1], matrix[7])[0,1]
    SLG_coef = np.corrcoef(matrix[2], matrix[8])[0,1]
    HRper_coef = np.corrcoef(matrix[3], matrix[9])[0,1]
    K_coef = np.corrcoef(matrix[4], matrix[10])[0,1]
    BB_coef = np.corrcoef(matrix[5], matrix[11])[0,1]
    #Average coefficent
    AVG_coef = np.mean([BA_coef, OBP_coef, SLG_coef, HRper_coef, K_coef, BB_coef])

    #Print the values
    print("\n")
    print("BA coefficent:", round(BA_coef, 3))
    print("OBP coefficent:",round(OBP_coef, 3))
    print("SLG coefficent:", round(SLG_coef, 3))
    print("HR% coefficent:", round(HRper_coef, 3))
    print("K% coefficent:", round(K_coef, 3))
    print("BB% coefficent:", round(BB_coef, 3))
    print("\n")
    print("Average coefficent:", round(AVG_coef, 3))
    print("\n")


#Loop through all of the pitcher files in the \Data\Pitchers dir
def main():
    for root, dirs, files in os.walk(os.getcwd()+'\Data\Batters'):
       for fname in files:
           run('Data\Batters\\' + fname)

    #Print the correlation matrix if debug is on
    if test_mode == True and debug == True:

        print(corr_matrix)

    if test_mode == True:
        correlation_test(corr_matrix)

main()