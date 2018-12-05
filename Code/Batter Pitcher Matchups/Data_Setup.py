import pandas as pd
import numpy as np

#Reads in and cleans the data, returns the three dataframes (events, pitchers, batters)
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
    events.columns = ['bID', 'pID', 'AVG', 'OBP', 'SLG', 'BBper', 'Kper']

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
    batters['bBBper'] = (batters['bBBper'].str.strip('%').astype(float))*0.01
    batters['bKper'] = (batters['bKper'].str.strip('%').astype(float))*0.01

    return events, pitchers, batters


#Standardizes the IDs across the different dataframes
def id_standardize(events, pitchers, batters):

    id_name_lookup = pd.read_csv("Data\\id_name_lookup.csv", encoding = "ISO-8859-1")

    retro_fg_convert = id_name_lookup[['fg_id', 'retro_id']]
    retro_fg_convert.columns = ['bID', 'retro_id']
    retro_fg_convert['bID'] = retro_fg_convert['bID'].str.encode('utf-8')
    retro_fg_convert['retro_id'] = retro_fg_convert['retro_id'].str.encode('utf-8')
    retro_fg_convert['bID'] = retro_fg_convert['bID'].str.decode('utf-8')
    retro_fg_convert['retro_id'] = retro_fg_convert['retro_id'].str.decode('utf-8')
    retro_fg_convert = retro_fg_convert[pd.to_numeric(retro_fg_convert['bID'], errors='coerce').notnull()]
    retro_fg_convert['bID'] = retro_fg_convert['bID'].astype(str).astype(int)

    batters = batters.merge(retro_fg_convert, on='bID', how='left')
    batters = batters[['retro_id', 'bName','bAVG', 'bOBP', 'bSLG', 'bBBper', 'bKper']]
    batters.columns = ['bID', 'bName','bAVG', 'bOBP', 'bSLG', 'bBBper', 'bKper']
    batters = batters.dropna(axis="rows")

    #Merge pitchers
    retro_bref_convert = id_name_lookup[['bref_id', 'retro_id']]
    retro_bref_convert.columns = ['pID', 'retro_id']
    retro_bref_convert['pID'] = retro_bref_convert['pID'].str.encode('utf-8')
    retro_bref_convert['retro_id'] = retro_bref_convert['retro_id'].str.encode('utf-8')
    retro_bref_convert['pID'] = retro_bref_convert['pID'].str.decode('utf-8')
    retro_bref_convert['retro_id'] = retro_bref_convert['retro_id'].str.decode('utf-8')

    pitchers = pitchers.merge(retro_bref_convert, on='pID', how='left')
    pitchers = pitchers[['retro_id', 'pName','pAVG', 'pOBP', 'pSLG', 'pBBper', 'pKper']]
    pitchers.columns = ['pID', 'pName','pAVG', 'pOBP', 'pSLG', 'pBBper', 'pKper']
    pitchers = pitchers.dropna(axis="rows")

    return events, pitchers, batters

#Combine all of the data into one final dataframe
def combine_data(events, pitchers, batters):

    events = events.merge(pitchers, on='pID', how='left')
    events = events.merge(batters, on='bID', how='left')

    events = events[['pAVG', 'pOBP', 'pSLG', 'pBBper', 'pKper', 'bAVG', 'bOBP', 'bSLG', 'bBBper', 'bKper', 'AVG', 'OBP', 'SLG', 'BBper', 'Kper']]

    return events

def main():

    #Read in the data
    events, pitchers, batters = read_in_data()

    #Change all of the IDs to Retrosheets
    events, pitchers, batters = id_standardize(events, pitchers, batters)

    #Combine all the data into one dataframe
    events = combine_data(events, pitchers, batters)

    events.to_csv("Data\\events_with_stats.csv")


main()