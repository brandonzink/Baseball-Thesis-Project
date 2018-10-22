import pandas as pd
import numpy as np
import math

#The debug mode varaible
debug = True
#3 year MLB averages for: H/PA, BB/PA, K/PA, 2B/H, 3B/H, HR/H, SB/1B, CS/SB, via FanGraphs
MLB_averages = [0.226, 0.084, 0.216, 0.199, 0.020, 0.138,  0.093, 0.385]

class player_stats:
    BA = 0 #Bating average
    BBper = 1 #Walk percentaage
    Kper = 2 #Strikeout percentage
    DoublePer = 3 #Double percentage (of hits)
    TriplePer = 4 #Triple percentage (of hits)
    HRper = 5 #Homerun percentage (of hits)
    SBper = 6 #Stolen base percentage (given a hit)
    CSper = 7 #Caught stealing percentage
    wOBA = 8

#Reads a .csv into a pandas dataframe, flips it vertically (so newer games are at the top),
#And removes the % signs from BB% and K% and turns them into a 0.00 style percentage instead of a
#00%. 
def read_data(filepath):
    data = pd.read_csv(filepath).iloc[::-1]
    data['BB%'] = (data['BB%'].str.strip('%').astype(float))*0.01
    data['K%'] = (data['K%'].str.strip('%').astype(float))*0.01
    return data

# Calculates the weight of the stats for a given game using an exponential method that
# weights more recent games higher than older games, maxing at 500 games
def weight_calculator(game_number):
    return (((9**(1./500.))**((game_number*-1.)+500))-1)

#Returns a numpy array of fully adjusted statistics given the sample size (games), weighted based on recency. The format
#of the array is as follows:
#[BA, BB%, K%, 2B%, 3B%, HR%, SB%, CS%, wOBA]
def calc_true_stats(data):
    
    #Data holders
    true_stats = np.zeros((9, 1))  #The final array to be returned
    true_stats_temp = np.zeros((9, 1)) #A placeholder array used for temporary data storage
    true_stats_PA = 0. #The number of weighted PA, used to divide the temp data storage by

    num_rows = len(data.index) #The number of rows in the dataframe

    max_index = min(500, num_rows) #The number of games, will max out at 500

    #Loop through the data and calculate the weighted raw statistics using the weight_calulator function
    for index, row in data.iterrows():
        if index <= 500: #Only consider the most recent 500 games max

            #Calculate the weight for this game so that we only have to do it once
            weight = weight_calculator(index)

            #Calculate the raw number for each stat
            true_stats_temp[player_stats.BA] += row['H']*weight #Hits
            true_stats_temp[player_stats.BBper] += (row['BB%']*row['PA'])*weight #Walks
            true_stats_temp[player_stats.Kper] += (row['K%']*row['PA'])*weight #Strikeouts
            true_stats_temp[player_stats.DoublePer] += row['2B']*weight #Doubles
            true_stats_temp[player_stats.TriplePer] += row['3B']*weight #Triples
            true_stats_temp[player_stats.HRper] += row['HR']*weight #Homeruns
            true_stats_temp[player_stats.SBper] += row['SB']*weight #Stolen bases
            true_stats_temp[player_stats.CSper] += row['CS']*weight #Caught stealng

            #The weighted plate appearances
            true_stats_PA += row['PA']*weight
    
    #Calculate their adjusted stats, unweighted for games at this point
    true_stats[player_stats.BA] = true_stats_temp[player_stats.BA]/true_stats_PA #BA, H/PA
    true_stats[player_stats.BBper] = true_stats_temp[player_stats.BBper]/true_stats_PA #BB%, BB/PA
    true_stats[player_stats.Kper] = true_stats_temp[player_stats.Kper]/true_stats_PA #K%, K/PA
    true_stats[player_stats.DoublePer] = true_stats_temp[player_stats.DoublePer]/true_stats_temp[player_stats.BA] #2B%, 2B/H
    true_stats[player_stats.TriplePer] = true_stats_temp[player_stats.TriplePer]/true_stats_temp[player_stats.BA] #3B%, 3B/H
    true_stats[player_stats.HRper] = true_stats_temp[player_stats.HRper]/true_stats_temp[player_stats.BA] #HR%, HR/H
    true_stats[player_stats.SBper] = true_stats_temp[player_stats.SBper]/(true_stats_temp[player_stats.BA]-(true_stats_temp[player_stats.DoublePer]+true_stats_temp[player_stats.TriplePer]+true_stats_temp[player_stats.HRper])) #SB%, SB/(H-(2B+3B+HR))
    true_stats[player_stats.CSper] = true_stats_temp[player_stats.CSper]/true_stats_temp[player_stats.SBper] #CS%, CS/SB

    ##DOUBLE CHECK THIS WOBA CALCULATION, ADJUST THE ONE BELOW TOO
    true_stats[player_stats.wOBA] = (((true_stats[player_stats.BA]-(true_stats[player_stats.DoublePer]+true_stats[player_stats.TriplePer]+true_stats[player_stats.HRper]))*0.888)+(true_stats[player_stats.BBper]*0.69)+((true_stats[player_stats.DoublePer]*true_stats[player_stats.BA])*1.271)+((true_stats[player_stats.TriplePer]*true_stats[player_stats.BA])*1.616)+((true_stats[player_stats.HRper]*true_stats[player_stats.BA])*1.616))

    #Check for NaN numbers, change to 0
    for i in range(0,8):
        if np.isnan(true_stats[i]):
            true_stats[i] = 0.

    #Prints out the unadjusted (for number of games) statistics if debug mode is on
    if debug == True:
        print("----------------")
        print("Unadjusted statistics")
        print("Games: ", max_index)
        print("uaBA: ", true_stats[0])
        print("uaBB%: ", true_stats[1])
        print("uaK%: ", true_stats[2])
        print("ua2B%: ", true_stats[3])
        print("ua3B%: ", true_stats[4])
        print("uaHR%: ", true_stats[5])
        print("uaSB%: ", true_stats[6])
        print("uaCS%: ", true_stats[7])
        print("uawOBA: ", true_stats[8])
        print("----------------")
        print("")

    #Adjust for the number of games in the sample size
    for i in range(0,8):
        true_stats[i] = ((max_index/500)*true_stats[i])+((1-(max_index/500))*MLB_averages[i])

    true_stats[player_stats.wOBA] = (((true_stats_temp[player_stats.BA]-(true_stats_temp[player_stats.DoublePer]+true_stats_temp[player_stats.TriplePer]+true_stats_temp[player_stats.HRper]))*0.888)+(true_stats[player_stats.BBper]*0.69)+(true_stats[player_stats.DoublePer]*true_stats[player_stats.BA]*1.271)+(true_stats[player_stats.TriplePer]*true_stats[player_stats.BA]*1.616)+(true_stats[player_stats.HRper]*true_stats[player_stats.BA]*1.616))


    #Prints out the adjusted (for number of games) statistics if debug mode is on
    if debug == True:
        print("----------------")
        print("Adjusted statistics")
        print("Games: ", max_index)
        print("aBA: ", true_stats[0])
        print("aBB%: ", true_stats[1])
        print("aK%: ", true_stats[2])
        print("a2B%: ", true_stats[3])
        print("a3B%: ", true_stats[4])
        print("aHR%: ", true_stats[5])
        print("aSB%: ", true_stats[6])
        print("aCS%: ", true_stats[7])
        print("awOBA: ", true_stats[8])
        print("----------------")

    #Return the array with the fully adjusted stats
    return true_stats

test_stats = read_data("Data/ChristianYelichGameLog.csv")
calc_true_stats(test_stats)




