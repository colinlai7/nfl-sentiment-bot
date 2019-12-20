import sys
import io
import datetime
import math
import os.path
from nltk.sentiment.vader import SentimentIntensityAnalyzer as SIA
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from driver import *

comment_df = pd.DataFrame([], columns = comment_df_columns)

def update_sentiment(path):
    global comment_df
    fullpath = 'game_comment_dfs/'+path+'.csv'
    # Read given file
    if os.path.isfile(fullpath):
        comment_df = pd.read_csv(fullpath)[comment_df_columns]
        print("Read " + fullpath)
    else:
        print(path + " was not found")
        return
    # Update polaraities for each comment
    polarities = []
    sia = SIA()
    for comment in comment_df['body']:
        pol_score = sia.polarity_scores(comment)
        polarities.append(pol_score['compound'])
    assert len(polarities) == len(comment_df)
    # assign new column and save it to CSV
    comment_df['polarity'] = polarities
    print(comment_df.head())
    comment_df.to_csv(fullpath)
    print('Succesfully updated polarities for ' + path + ' to CSV')

def avg_over_time(path):
    post_df = pd.read_csv("post_df.csv")[post_df_columns]
    fullpath = 'game_comment_dfs/'+path+'.csv'
    comment_df = pd.read_csv(fullpath)[['body', 'author_flair_text', 'score', 'created_utc', 'link_id', 'polarity']]
    game_vars = path.split('_')
    team_1 = game_vars[2]
    team_2 = game_vars[3]
    # set time limit to 5 hours after game start
    start_time = post_df[post_df['link_id']==game_vars[1]]['created_utc'].values[0]
    print(start_time)
    time_limit = start_time + 18000
    # intialize graph_data
    graph_data = pd.DataFrame(0.0, index=range(30), columns=[team_1 +' sum', team_2+' sum', 'Everyone else sum', team_1+' cnt', team_2+' cnt', 'Everyone else cnt'])
    # print(graph_data.shape)
    for idx in comment_df.index:
        # print(comment_df['created_utc'][idx])
        # print(comment_df.loc[idx, 'created_utc'])
        # print(time_limit)
        if comment_df.loc[idx, 'created_utc'] >= time_limit:
            continue
        com_pol = comment_df['polarity'][idx]
        print(com_pol)
        com_tm = comment_df['author_flair_text'][idx]
        com_idx = int((comment_df['created_utc'][idx] - start_time) / 600)
        # print(com_idx)
        # Data for 2 teams in the game
        if (com_tm == team_1) or (com_tm == team_2):
            graph_data.loc[com_idx][com_tm+' sum'] += float(com_pol)
            graph_data.loc[com_idx][com_tm+' cnt'] += 1
        # Everyone else data
        else:
            graph_data.loc[com_idx]['Everyone else sum'] += float(com_pol)
            graph_data.loc[com_idx]['Everyone else cnt'] += 1
    utcs = [start_time + (i * 600) for i in range(30)]
    graph_data['utcs'] = utcs
    print(graph_data.head())
    graph_data.to_csv('graph_data.csv')




    # print("before and after")
    print(len(comment_df))
    # post_df = post_df[post_df['created_utc']. < time_limit]
    # print(len(comment_df[comment_df['created_utc'] < pd.Series([time_limit] * len(comment_df))]))
    # print(start_time)



test_path = 'week11_dxpi00_Broncos_Vikings'
# update_sentiment(test_path)
avg_over_time(test_path)
