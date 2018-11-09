import pandas as pd
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.linear_model import LinearRegression
import statsmodels.formula.api as smf

def import_data():

    Two_wk_advanced = pd.read_csv("Data\\2wk_Advanced_Stats.csv")
    Two_wk_batted = pd.read_csv("Data\\2wk_Batted_Ball.csv")
    
    ROS_advanced = pd.read_csv("Data\\ROS_Advanced_Stats.csv")
    ROS_batted = pd.read_csv("Data\\ROS_Batted_Ball.csv")

    Two_wk_cols_to_use = Two_wk_advanced.columns.difference(Two_wk_batted.columns)
    ROS_cols_to_use = ROS_advanced.columns.difference(ROS_batted.columns)

    df_Two_wk = pd.merge(Two_wk_batted, Two_wk_advanced[Two_wk_cols_to_use], left_index=True, right_index=True, how='outer')
    df_ROS = pd.merge(ROS_batted, ROS_advanced[ROS_cols_to_use], left_index=True, right_index=True, how='outer')

    columns = list(df_ROS)

    print(df_Two_wk)

    batter_data = pd.merge(df_ROS, df_Two_wk, suffixes=('_ROS','_Two_wk'))

    #Two_wk_advanced = Two_wk_advanced.join(Two_wk_batted, on = 'playerId')
    #ROS_advanced = ROS_advanced.join(ROS_batted, on = 'playerId')

    return batter_data, columns

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

def main():

    batter_data, columns = import_data()

    print(list(batter_data))


    #model = forward_select(ROS_data, Two_week_data['AVG'], 5)

    #model = smf.ols(formula="rec_BA ~ BA + OBP + SLG + HRper + Kper + BBper", data=batters).fit()

    #print(model.summary())

    #print(batters[batters.columns[:7]])


main()