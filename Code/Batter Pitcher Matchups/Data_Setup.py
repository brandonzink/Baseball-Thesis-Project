import pandas as pd
import numpy as np

def read_in_data():

    #Read in all events data and parse out needed columns
    events1 = pd.read_csv("Data\\events1.csv")
    events2 = pd.read_csv("Data\\events2.csv")
    events3 = pd.read_csv("Data\\events3.csv")
    events4 = pd.read_csv("Data\\events4.csv")
    events5 = pd.read_csv("Data\\events5.csv")
    events6 = pd.read_csv("Data\\events6.csv")
    events7 = pd.read_csv("Data\\events7.csv")

    events_temp = pd.concat([events1, events2, events3, events4, events5, events6, events7])
    events_temp['AVG'] = np.where(events_temp[' H_CD']>0, 1, 0)
    events_temp['OBP'] = np.where(events_temp[' BAT_DEST_ID']>0, 1, 0)
    events_temp['SLG'] = events_temp[' BAT_DEST_ID']
    events_temp['BBper'] = np.where(events_temp[' EVENT_CD']==14, 1, 0)
    events_temp['Kper'] = np.where(events_temp[' EVENT_CD']==3, 1, 0)

    events = events_temp[[' BAT_ID', ' PIT_ID', 'AVG', 'OBP', 'SLG', 'BBper', 'Kper']]
    events.columns = ['BAT_ID', 'PIT_ID', 'AVG', 'OBP', 'SLG', 'BBper', 'Kper']

    #Read in pitcher data, remove duplicates, parse out needed columns
    pitchers_temp = pd.read_csv('Data\\pitcher_stats.csv')

    pitchers_temp = pitchers_temp.drop_duplicates(subset='Name', keep='first')
    pitchers_temp['ID'] = pitchers_temp['Name'].str.split('\\').str[1]
    pitchers_temp['Name'] = pitchers_temp['Name'].str.split('\\').str[0]
    pitchers_temp['Name'] = pitchers_temp['Name'].str.replace('*', '')
    pitchers_temp['BBper'] = pitchers_temp['BB']/pitchers_temp['PA']
    pitchers_temp['Kper'] = pitchers_temp['SO']/pitchers_temp['PA']

    pitchers = pitchers_temp[['ID', 'Name', 'BA', 'OBP', 'SLG', 'BBper', 'Kper']]
    pitchers.columns = ['pID', 'pName','pAVG', 'pOBP', 'pSLG', 'pBBper', 'pKper']

    #Read in batter data, parse out needed columns
    batters_temp = pd.read_csv('Data\\batter_stats.csv')

    batters = batters_temp[['playerid', 'Name', 'AVG', 'OBP', 'SLG', 'BB%', 'K%']]
    batters.columns=['bID', 'bName', 'bAVG', 'bOBP', 'bSLG', 'bBBper', 'bKper']

    return events, pitchers, batters




def main():

    #NOTE: events (and therefore IDs) are pulled from Retrosheet. Batters are pulled from FanGraphs. Pitchers are pulled from BBR.

    events, pitchers, batters = read_in_data()


main()