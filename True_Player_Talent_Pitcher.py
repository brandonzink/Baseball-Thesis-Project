import pandas as pd
import numpy as np
import math

#The debug mode varaible
debug = True
#3 year MLB averages for: H/PA, BB/PA, K/PA, HR/H via FanGraphs
MLB_averages = [0.226, 0.084, 0.199, 0.138]

class player_stats:
    BA = 0 #Bating average
    BBper = 1 #Walk percentaage
    Kper = 2 #Strikeout percentage
    HRper = 3 #Homerun percentage (of hits)

#Reads a .csv into a pandas dataframe, flips it vertically (so newer games are at the top),
#And removes the % signs from BB% and K% and turns them into a 0.00 style percentage instead of a
#00%. 
def read_data(filepath):
    data = pd.read_csv(filepath).iloc[::-1]
    data['BB%'] = (data['BB%'].str.strip('%').astype(float))*0.01
    data['K%'] = (data['K%'].str.strip('%').astype(float))*0.01
    return data

