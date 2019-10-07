import sys
import io
import praw
import datetime
import keys
import pandas as pd
from datetime import datetime
startTime = datetime.now()
from praw.models import MoreComments

reddit = praw.Reddit(client_id=keys.client_id,
                     client_secret=keys.client_secret,
                     user_agent='my user agent')

# use unicode encoding
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding = 'utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding = 'utf-8')

def test():
    test = 1
    cols = ['body', 'flair', 'score', 'comment_time', 'post_time', 'post_title']
    df = pd.DataFrame([], columns = cols)

    # iterate through nfl_gamethread posts
    for submission in reddit.redditor('nfl_gamethread').submissions.new(limit=200):
        # filter by game thread posts
        if submission.title.startswith("Game Thread") and ("RedZone" not in submission.title):
            # filter by date
            print(submission.title)
            post_date_time = datetime.utcfromtimestamp(submission.created_utc)#.strftime('%Y-%m-%d %H:%M:%S')
            # iterate through a game thread's comments
            for top_level_comment in submission.comments:
                if isinstance(top_level_comment, MoreComments):
                    continue
                com = top_level_comment
                com_date_time = datetime.utcfromtimestamp(com.created_utc)
                # com_string = top_level_comment.body
                # attributes = top_level_comment.__dict__
                # for item in attributes:
                #     print(item)
                #     print(attributes[item])
                # print(top_level_comment.author_flair_css_class)
                # break

                tempdf = pd.DataFrame([[com.body, com.author_flair_css_class,
                                com.score, com_date_time, post_date_time,
                                submission.title]], columns=cols)
                df = df.append(tempdf, ignore_index = True)
                # print(com_string)
            break
    print(df.head())
    print(df['post_time'].unique())
    print(len(df))
    #
    #         print(count)
    #         print(df)
    #         print(datetime.now() - startTime)
    #         # file.close()
    #     test += 1

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

test()
