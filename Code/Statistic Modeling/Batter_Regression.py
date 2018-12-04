import pandas as pd
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.linear_model import LinearRegression
import statsmodels.formula.api as smf


#Reads in the data, combines it into one dataframe (no suffix is ROS, last two weeks have suffix _two_wk)
#Returns the dataframe and a list of the column headers for the ROS stats
def import_data():

    Two_wk_advanced = pd.read_csv("Data\\2wk_Advanced_Stats.csv")
    Two_wk_batted = pd.read_csv("Data\\2wk_Batted_Ball.csv")
    
    ROS_advanced = pd.read_csv("Data\\ROS_Advanced_Stats.csv")
    ROS_batted = pd.read_csv("Data\\ROS_Batted_Ball.csv")

    Two_wk_advanced.columns = Two_wk_advanced.columns.str.replace(r"[%]", "per")
    Two_wk_batted.columns = Two_wk_batted.columns.str.replace(r"[%]", "per")

    ROS_advanced.columns = ROS_advanced.columns.str.replace(r"[%]", "per")
    ROS_batted.columns = ROS_batted.columns.str.replace(r"[%]", "per")

    Two_wk_advanced.columns = Two_wk_advanced.columns.str.replace(r"[/]", "per")
    Two_wk_batted.columns = Two_wk_batted.columns.str.replace(r"[/]", "per")

    ROS_advanced.columns = ROS_advanced.columns.str.replace(r"[/]", "per")
    ROS_batted.columns = ROS_batted.columns.str.replace(r"[/]", "per")

    Two_wk_cols_to_use = Two_wk_advanced.columns.difference(Two_wk_batted.columns)
    ROS_cols_to_use = ROS_advanced.columns.difference(ROS_batted.columns)

    df_Two_wk = pd.merge(Two_wk_batted, Two_wk_advanced[Two_wk_cols_to_use], left_index=True, right_index=True, how='outer')
    df_ROS = pd.merge(ROS_batted, ROS_advanced[ROS_cols_to_use], left_index=True, right_index=True, how='outer')

    columns = list(df_ROS)

    batter_data = pd.merge(df_ROS, df_Two_wk, on='playerId', how='inner', suffixes=('','_two_wk'))

    return batter_data, columns

#Forward selecting linear regression model
#Returns the model
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

#Runs the regression and prints the model
#Takes in the dataframe, list of columns in ROS, the column from the two weeks to regress on, and the max number of columns to use
def regression(data, columns, regressed_column, maxk):
    
    columns.append(regressed_column)
    columns.remove('Season')
    columns.remove('Tm')
    columns.remove('playerId')
    columns.remove('Name')

    temp_batters = data[columns]

    model = forward_select(temp_batters, regressed_column, maxk)

    print(model.summary())

def main():

    batter_data, columns = import_data()

    regression(batter_data, columns, 'BBper_two_wk', 5)



main()