import pandas as pd
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import PolynomialFeatures
import statsmodels.formula.api as smf
import statsmodels.api as sm


#Normalizes each column in a dataframe input
def normalize(df):
    result = df.copy()
    for feature_name in df.columns:
        max_value = df[feature_name].max()
        min_value = df[feature_name].min()
        result[feature_name] = (df[feature_name] - min_value) / (max_value - min_value)
    return result

#Reads in the data, returns dataframe
def read_in_data():

    data = pd.read_csv("Data\\events_with_stats.csv")
    data = data.dropna(axis="rows")
    data = data.drop('pID', 1)
    data = data.drop('bID', 1)

    return data

#Calculates the expected outcomes for each stat using the Odds Ratio Method, returns dataframe with player
#stats and diff in stats (column header will begin with "d")
def calculate_expected_values(data):

    #The MLB averages for AVG, OBP, SLG, BB%, K%
    MLB_averages = [0.248, 0.318, 0.409, 0.085, 0.223]

    #Calculate the expected values for each matchup
    data['eAVG'] = odds_ratio_method(data['bAVG'], data['pAVG'], MLB_averages[0])
    data['eOBP'] = odds_ratio_method(data['bOBP'], data['pOBP'], MLB_averages[1])
    data['eSLG'] = odds_ratio_method(data['bSLG'], data['pSLG'], MLB_averages[2])
    data['eBBper'] = odds_ratio_method(data['bBBper'], data['pBBper'], MLB_averages[3])
    data['eKper'] = odds_ratio_method(data['bKper'], data['pKper'], MLB_averages[4])

    #Calculate the difference (expected - actual)
    data['dAVG'] = data['eAVG'] - data['AVG']
    data['dOBP'] = data['eOBP'] - data['OBP']
    data['dSLG'] = data['eSLG'] - data['SLG']
    data['dBBper'] = data['eBBper'] - data['BBper']
    data['dKper'] = data['eKper'] - data['Kper']

    #Select the columns we want and return the dataframe
    return data[['pAVG', 'pOBP', 'pSLG', 'pBBper', 'pKper', 'bAVG', 'bOBP', 'bSLG', 'bBBper', 'bKper', 'dAVG', 'dOBP', 'dSLG', 'dBBper', 'dKper']]


#Uses the Odds Ratio MEthod to calculate the expected outcome
def odds_ratio_method(b_stat, p_stat, mlb_avg):

    odds_b = b_stat/(1-b_stat)
    odds_p = p_stat/(1-p_stat)
    odds_l = mlb_avg/(1-mlb_avg)
    odds = (odds_b*odds_p)/odds_l
    rate = odds/(1+odds)
    
    return rate

#Forward selecting linear regression model, returns the model
def forward_select(df, resp_str , maxk):
    
    remaining = set(df.columns)
    remaining.remove(resp_str)
    selected = []
    numselected = 1
    score_crnt, score_new = 0.0, 0.0
    while remaining and score_crnt == score_new:
        score_array = []
        for candidate in remaining:
            formula = "{} ~ {} + 1".format(resp_str,' + '.join(selected + [candidate]))
            score = smf.ols(formula, df).fit().rsquared_adj
            score_array.append((score, candidate))
        score_array.sort()
        score_new, best_option = score_array.pop()
        if score_crnt < score_new and numselected <= maxk:
            remaining.remove(best_option)
            selected.append(best_option)
            score_crnt = score_new
            numselected += 1
    formula = "{} ~ {} + 1".format(resp_str,' + '.join(selected))
    model = smf.ols(formula, df).fit()
    return model

def run_regression_base(data, reg_column):

    columns = ['pAVG', 'pOBP', 'pSLG', 'pBBper', 'pKper', 'bAVG', 'bOBP', 'bSLG', 'bBBper', 'bKper']

    columns.append(reg_column)

    temp_data = data[columns]

    model = forward_select(temp_data, reg_column, 4)

    print(model.summary())


def main():

    data = read_in_data()

    data = calculate_expected_values(data)

    run_regression_base(data, 'dBBper')


main()