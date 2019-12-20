import sys
import io
import praw
import datetime
import keys
import requests
import math
import os.path
import pandas as pd
from datetime import datetime
from praw.models import MoreComments

startTime = datetime.now()

reddit = praw.Reddit(client_id=keys.client_id,
                     client_secret=keys.client_secret,
                     user_agent='my user agent')

# use unicode encoding
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding = 'utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding = 'utf-8')

# dataframes
post_df_columns = ['link_id', 'post_title', 'team_1', 'team_2', 'created_utc']
post_df = pd.DataFrame([], columns = post_df_columns)
comment_df_columns = ['body', 'author_flair_text', 'score', 'created_utc', 'link_id']
comment_df = pd.DataFrame([], columns = comment_df_columns)

# team names set
team_names = ['49ers', 'Bears', 'Bengals', 'Bills', 'Broncos', 'Browns', 'Buccaneers', 'Cardinals',
'Chargers', 'Chiefs', 'Colts', 'Cowboys', 'Dolphins', 'Eagles', 'Falcons', 'Giants',
'Jaguars', 'Jets', 'Lions', 'Packers', 'Panthers', 'Patriots', 'Raiders', 'Rams',
'Ravens', 'Redskins', 'Saints', 'Seahawks', 'Steelers', 'Texans', 'Titans', 'Vikings']


season_start = 1567641600
# week_times = [1567641600 + (i * 604800)  for i in range(22)] # 9/5 1567641600 9/12

def fetch_old_threads():
    global post_df
    # testing one thread
    post_limit = 1
    # iterate through nfl_gamethread posts
    for submission in reddit.redditor('nfl_gamethread').submissions.new(limit=200):
        # testing: only do one thread
        # if post_limit > 3:
        #     break
        if submission.title.startswith("Game Thread") and ("RedZone" not in submission.title):
            # end program once submissions before season start are reached
            assert submission.created_utc > season_start
            # If post already in post dataframe, don't add it
            # if not, populate it
            if submission.id not in post_df['link_id'].values:
                # get the teams from the title
                thread_teams = []
                for team in team_names:
                    if team in submission.title:
                        thread_teams.append(team)
                # assert only two teams per game
                assert len(thread_teams) == 2
                new_post = pd.DataFrame([[submission.id, submission.title, thread_teams[0], thread_teams[1], submission.created_utc]], columns=post_df_columns)
                print("New post to append:")
                print(new_post)
                # post_df = post_df.append(new_post, ignore_index=True, sort=True)
                post_df = pd.concat([post_df, new_post], ignore_index=True, sort=False)

                # Pull first 500 comments and get last comment's UTC
                request_string = "https://api.pushshift.io/reddit/comment/search?link_id=" + submission.id + "&limit=500&sort=desc"
                json = requests.get(request_string, headers={'User-Agent': "AUniqueUserAgent"})
                comments = json.json()['data']
                df = pd.DataFrame(comments)
                # Continuously pull next 500 comments
                for x in range(0,500):
                    last_uct = comments[-1]['created_utc']
                    json = requests.get(request_string + "&before={}".format(last_uct), headers={'User-Agent': "AUniqueUserAgent"})
                    comments = json.json()['data']
                    df2 = pd.DataFrame(comments)
                    df = pd.concat([df, df2], ignore_index=True, sort=True)
                    try:
                        print('Last comment pulled: {}'.format(comments[-1]['body']))
                    except IndexError:
                        print('No More Comments to pull')
                        break
                    print('Timestamp: {}'.format(comments[-1]['created_utc']))
                    print('Number of comments pulled {}'.format(df.shape[0]))

                # Prune data to only relevant attributes of each comment
                df = df[['body', 'author_flair_text', 'score', 'created_utc']]
                df['link_id'] = submission.id
                # Get week of game
                week = math.ceil((submission.created_utc - season_start) / 604800)
                # print(type(submission.created_utc))
                df_name = "_".join(['week' + str(week), submission.id] + thread_teams)
                print(df_name)
                # Save data to CSVs
                df.to_csv('game_comment_dfs/' + df_name + '.csv')
                print('Succesfully saved ' + df_name + ' to CSV')
                post_df.to_csv('post_df.csv')
                print('Succesfully updated post_df to CSV')
                # print(df.head())
                post_limit += 1

def load_df():
    global post_df
    # if post_df not instantiated yet
    if os.path.isfile('post_df.csv'):
        post_df = pd.read_csv("post_df.csv")[post_df_columns]
        print("Read post_df.csv")
    else:
        post_df.to_csv('post_df.csv')
        print("Created new post_df.csv because it did not exist")
    # print(len(comment_df['author_flair_text'].unique()))
    print(len(post_df))
    print(post_df.head())
    print(post_df.columns)
    # test one thread's comments
    # print(post_df.loc[0]['link_id'])


# def main():


def catch_encoding_error(f, comment):
    for c in comment:
        print(c)
        f.write(c)

# main()
load_df()

fetch_old_threads()
