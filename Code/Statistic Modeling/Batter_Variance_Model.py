import pandas as pd
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.linear_model import LinearRegression
import statsmodels.formula.api as smf

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

#The stat to run this on
stat_analyzed = 'BA'

#Reads a .csv into a pandas dataframe, delete the "Totals" row, drop the % on the BB% and K% columns, sort so newest first, reindex
def read_data(filepath):
    data = pd.read_csv(filepath)
    data = data[~data['Date'].astype(str).str.startswith('T')]
    data['BB%'] = (data['BB%'].str.strip('%').astype(float))*0.01
    data['K%'] = (data['K%'].str.strip('%').astype(float))*0.01
    data = data.sort_values(by='Date', ascending=False)
    data = data.reset_index(drop=True)
    return data

def calc_stats(data):


#Run the program on a given file
def run(filename):
    print("Running on", filename)
    calc_stats(read_data(filename))

#Loop through all of the pitcher files in the \Data\Pitchers dir
def main():
    for root, dirs, files in os.walk(os.getcwd()+'\Data\Batters'):
       for fname in files:
           run_var('Player_Logs_Data\Batters\\' + fname)