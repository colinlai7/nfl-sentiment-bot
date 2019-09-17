import sys
import io
import praw
import keys
from praw.models import MoreComments

reddit = praw.Reddit(client_id=keys.client_id,
                     client_secret=keys.client_secret,
                     user_agent='my user agent')

# use unicode encoding
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding = 'utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding = 'utf-8')

def main():
    print(reddit.read_only)
    # open file to write to
    file = open("test.txt", "w", encoding = 'utf-8')
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
                    file.write(com_string)
                except:
                    err_count += 1
                    # catch_encoding_error(file, com_string)
                count += 1
            print(err_count)
            print(count)
            file.close()
        test += 1

def catch_encoding_error(f, comment):
    for c in comment:
        print(c)
        f.write(c)

main()
