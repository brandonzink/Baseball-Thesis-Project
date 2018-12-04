import pandas as pd
import numpy as np
import matplotlib.mlab as mlab
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.linear_model import LinearRegression
import statsmodels.formula.api as smf

def import_data():

    Two_wk_advanced = pd.read_csv("Data\\2wk_Advanced_Pitchers.csv")
    Two_wk_batted = pd.read_csv("Data\\2wk_Batted_Ball_Pitchers.csv")
    
    ROS_advanced = pd.read_csv("Data\\ROS_Advanced_Pitchers.csv")
    ROS_batted = pd.read_csv("Data\\ROS_Batted_Ball_Pitchers.csv")

    Two_wk_advanced.columns = Two_wk_advanced.columns.str.replace(r"[%]", "per")
    Two_wk_batted.columns = Two_wk_batted.columns.str.replace(r"[%]", "per")

    ROS_advanced.columns = ROS_advanced.columns.str.replace(r"[%]", "per")
    ROS_batted.columns = ROS_batted.columns.str.replace(r"[%]", "per")

    Two_wk_advanced.columns = Two_wk_advanced.columns.str.replace(r"[/]", "per")
    Two_wk_batted.columns = Two_wk_batted.columns.str.replace(r"[/]", "per")

    ROS_advanced.columns = ROS_advanced.columns.str.replace(r"[/]", "per")
    ROS_batted.columns = ROS_batted.columns.str.replace(r"[/]", "per")

    Two_wk_advanced.columns = Two_wk_advanced.columns.str.replace(r"[-]", "minus")
    Two_wk_batted.columns = Two_wk_batted.columns.str.replace(r"[-]", "minus")

    ROS_advanced.columns = ROS_advanced.columns.str.replace(r"[-]", "minus")
    ROS_batted.columns = ROS_batted.columns.str.replace(r"[-]", "minus")

    Two_wk_cols_to_use = Two_wk_advanced.columns.difference(Two_wk_batted.columns)
    ROS_cols_to_use = ROS_advanced.columns.difference(ROS_batted.columns)

    df_Two_wk = pd.merge(Two_wk_batted, Two_wk_advanced[Two_wk_cols_to_use], left_index=True, right_index=True, how='outer')
    df_ROS = pd.merge(ROS_batted, ROS_advanced[ROS_cols_to_use], left_index=True, right_index=True, how='outer')

    columns = list(df_ROS)

    pitcher_data = pd.merge(df_ROS, df_Two_wk, on='Name', how='inner', suffixes=('','_two_wk'))

    return pitcher_data, columns


def corr_test(data):

    data['eKper9'] = (data['Kper9']*29.32) + (data['Pullper']*-20.85) + (data['IFHper']*16.98) + 9.53
    print('K/9 Coeff:',data['eKper9'].corr(data['Kper9_two_wk']))

    data['eBBper9'] = (data['BBper']*21.39) + (data['LDper']*-14.04) + (data['TBF']*0.0024) + (data['Centper']*10.35) + (data['Softper']*-8.66) + 0.91
    print('BB/9 Coeff:',data['eBBper9'].corr(data['BBper9_two_wk']))

    data['eHRper9'] = (data['HRper9']*0.86) + (data['IFFBper']*5.42) + (data['Pullper']*-2.95) + 0.749
    print('HR/9 Coeff:',data['eHRper9'].corr(data['HRper9_two_wk']))


def main():

    batter_data, columns = import_data()

    corr_test(batter_data)


main()