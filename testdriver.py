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
week_times = [1567641600 + (i * 604800)  for i in range(22)] # 9/5 1567641600 9/12

def fetch_old_threads():
    global post_df
    # testing one thread
    post_limit = 0
    # iterate through nfl_gamethread posts
    for submission in reddit.redditor('nfl_gamethread').submissions.new(limit=100):
        # testing: only do one thread
        if post_limit > 20:
            break
        if submission.title.startswith("Game Thread") and ("RedZone" not in submission.title):
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
                post_df = pd.concat([post_df, new_post], sort=False)


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
                    df = pd.concat([df, df2], sort=True)
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


def test():
    cols = ['body', 'flair', 'score', 'comment_time', 'post_time', 'post_title']
    df = pd.DataFrame([], columns = cols)
    submission_count = 0
    # iterate through nfl_gamethread posts
    for submission in reddit.redditor('nfl_gamethread').submissions.new(limit=100):
    # test single submission
    # if True:
        submission = reddit.submission(id='e58p5d')
        print(submission.title)
        # filter by game thread posts
        if submission.title.startswith("Game Thread") and ("RedZone" not in submission.title) and ("Vikings" in submission.title) and ("Seahawks" in submission.title):
            # submission = reddit.submission(id='dervtm')
            submission_count += 1
            print(submission.title)
            print(submission.id)
            print(submission.num_comments)
            post_date_time = datetime.utcfromtimestamp(submission.created_utc)#.strftime('%Y-%m-%d %H:%M:%S')
            # filter by date to only include starting 2019 season
            # if post_date_time.day < 5 and post_date_time.month < 9 and post_date_time.year < 2019:
            #     continue
            count = 0
            # replace MoreComments with comments
            # not_replaced = submission.comments.replace_more(limit=None)#, threshold=1)

            # iterate through submission's comments via breadth first traversal
            # print(len(submission.comments.list()))
            # comment_queue = submission.comments[:]  # Seed with top-level
            # while comment_queue:
            #     com = comment_queue.pop(0)
            #     # print(comment.body)
            #     comment_queue.extend(com.replies)
            # break
            # submission.comments.replace_more(limit=None)
            # for com in submission.comments.list():
            #     # print(count)
            #     count += 1
            #     com_date_time = datetime.utcfromtimestamp(com.created_utc)
                # get attributes
                # attributes = top_level_comment.__dict__
                # for item in attributes:
                #     print(item)
                #     print(attributes[item])
                # tempdf = pd.DataFrame([[com.body, com.author_flair_css_class,
                #                 com.score, com_date_time, post_date_time,
                #                 submission.title]], columns=cols)
                # df = df.append(tempdf, ignore_index = True)
            print(count)
        # if submission_count > 0:
        #     break
            # # break after one
            # break
    # df.to_csv('testcsv')
    # print(df['post_time'].unique())
    print(count)
    # print(len(df))


def main():
    print(reddit.read_only)
    # open file to write to
    # file = open("test.txt", "w", encoding = 'utf-8')
    test = 1
    for submission in reddit.subreddit('nfl').hot(limit=3):
        count = 0
        err_count = 0
        if test == 3:
            for top_level_comment in submission.comments:
                if isinstance(top_level_comment, MoreComments):
                    continue
                com_string = top_level_comment.body
                try:
                    print(com_string)

                    # file.write(com_string)
                except:
                    err_count += 1
                    # catch_encoding_error(file, com_string)
                count += 1
            print(err_count)
            print(count)
            # file.close()
        test += 1

def catch_encoding_error(f, comment):
    for c in comment:
        print(c)
        f.write(c)

# main()
load_df()

fetch_old_threads()
