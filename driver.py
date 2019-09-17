import praw
import keys
from praw.models import MoreComments

reddit = praw.Reddit(client_id=keys.client_id,
                     client_secret=keys.client_secret,
                     user_agent='my user agent')


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
                com_string = top_level_comment.body #.encode('cp1252').decode('cp1252').encode('UTF-8')
                # break
                file.write(com_string)
                try:
                    print(com_string)
                    file.write(com_string)
                except:
                    err_count += 1
                count += 1
            print(err_count)
            print(count)
            file.close()
        test += 1

main()
