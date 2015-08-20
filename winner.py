#!/usr/bin/env python

from libocho.Twitter import Twitter
from libocho.PSQL import PSQL
from libocho.Util import (
    out,
    err
)
from sys import exit
from threading import (
    Timer,
    Lock
)
from time import sleep

def main():
    args = parse_args()

    # t = Twitter API, p = PSQL Helper Functions
    t = Twitter(args.configPath)
    p = PSQL(args.configPath)

    # Contests Queue
    contests = []

    # Create Mutex Lock
    mutex = Lock()

    def update_queue():
        # Setup and start the threading
        u = Timer(60.0 * 5.0, update_queue)
        u.daemon = True
        u.start()

        mutex.acquire()
        try:
            if len(contests) > 0:
                contest = contests[0]
                out("Contest: %s" % contest['text'])

                followed = check_for_follow_request(contest, t, p)
                favourited = check_for_favourite_request(contest, t, p)
                retweet_post(contest, t, p, followed, favourited)

                contests.pop(0)
        finally:
            mutex.release()

    def scan_for_contests():
        # Setup and start the threading
        v = Timer(60.0 * 10.0, scan_for_contests)
        v.daemon = True
        v.start()

        mutex.acquire()
        try:
            out("Scanning For Contests...")
            last_twitter_id = p.get_last_twitter_id()

            try:
                #"RT to win" music OR sound OR speaker OR dj OR mixer OR gear'
                results = t.api.GetSearch(
                    term='"RT to win"',
                    since_id=last_twitter_id
                )

                for status in results:
                    item = status.AsDict()
                    if 'retweet_count' in item and item['retweet_count'] > 0:
                        if item['id'] > last_twitter_id:
                            p.set_last_twitter_id(item['id'])
                            contests.append(item)
            except Exception as e:
                err("[scan_for_contests] Search Error: %s" % e)
        finally:
            mutex.release()

    scan_for_contests()
    update_queue()

    try:
        while 1:
            sleep(1)
    except KeyboardInterrupt as e:
        out("Closing...")

    exit(0)


def retweet_post(item, twitter, psql, followed, favourited):
    out("Retweeting...")

    # Check if we have already retweeted this post
    retweeted = False
    try:
        tweet_id = item['retweeted_status']['id']
        if not psql.check_contest(tweet_id):
            retweeted = True
            twitter.api.PostRetweet(tweet_id)
    except Exception as e:
        retweeted = False
        try:
            tweet_id = item['id']
            if not psql.check_contest(tweet_id):
                retweeted = True
                twitter.api.PostRetweet(item['id'])
        except Exception as e:
            retweeted = False

    if retweeted:
        psql.add_contest(
            tweet_id,
            item['text'],
            item['user']['screen_name'],
            followed,
            favourited
        )


def check_for_follow_request(item, twitter, psql):
    """
    Check if a post requires you to follow the user.
    Be careful with this function! Twitter may write ban your application for
    following too aggressively
    """
    followed = False
    text = item['text']
    if 'follow' in text.lower():
        out("Asking to follow...")
        followed = True

        # Unfollow oldest follower if our follower count is >= 1900
        follower_count = psql.get_follower_count()
        if follower_count >= 1900:
            oldest_follower = psql.get_oldest_follower()
            out("Too many followers: Unfollowing %s" % oldest_follower)

            # Unfollow that nerd
            twitter.api.DestroyFriendship(
                screen_name=oldest_follower
            )
            psql.unfollow_user(oldest_follower)


        # Follow the new guy
        try:
            new_follower = item['retweeted_status']['user']['screen_name']
            twitter.api.CreateFriendship(
                screen_name=new_follower
            )
        except Exception as e:
            new_follower = item['user']['screen_name']
            twitter.api.CreateFriendship(
                screen_name=new_follower
            )

        # Add follower to db
        psql.follow_user(new_follower)
    return followed


def check_for_favourite_request(item, twitter, psql):
    """
    Check if a post requires you to favourite the tweet.
    Be careful with this function! Twitter may write ban your application for
    favouriting too aggressively
    """
    favourited = False
    text = item['text']
    # Check both canadian and american spelling
    if 'favourite' in text.lower() or 'favorite' in text.lower():
        out("Asking to favourite...")

        # Check if we have already favourited
        if not psql.check_favourite(item['id']):
            favourited = True
            try:
                twitter.api.CreateFavorite(
                    id=item['retweeted_status']['user']['id']
                )
            except Exception as e:
                twitter.api.CreateFavorite(
                    id=item['id']
                )

    return favourited


def parse_args():
    import argparse
    parser = argparse.ArgumentParser(
        description="You are winner HAHAHA",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        'configPath',
        type=str,
        help="Path to config file"
    )

    return parser.parse_args()


if __name__ == "__main__":
    main()
