#!/usr/bin/env python

from libocho.Twitter import Twitter
from libocho.PSQL import PSQL
from libocho.Util import (
    out,
    err
)
from sys import exit

import threading
import time

def main():
    args = parse_args()

    # t = Twitter API, p = PSQL Helper Functions
    t = Twitter(args.configPath)
    p = PSQL(args.configPath)

    contests = []

    out('Ahh')

    def update_queue():
        # Setup and start the threading
        u = threading.Timer(3, update_queue)
        u.daemon = True
        u.start()

        if len(contests) > 0:
            contest = contests[0]
            out("Contest: %s" % contest['text'])

            followed = check_for_follow_request(contest, t, p)
            favourited = check_for_favourite_request(contest, t, p)
            retweet_post(contest, t, p, followed, favourited)

            contests.pop(0)


    def scan_for_contests():
        # Setup and start the threading
        v = threading.Timer(10.0, scan_for_contests)
        v.daemon = True
        v.start()

        out("Scanning For Contests...")
        last_twitter_id = p.get_last_twitter_id()

        try:
            results = t.api.GetSearch(
                term="RT to win",
                since_id=last_twitter_id
            )

            for status in results:
                item = status.AsDict()
                if item['retweet_count'] > 0:
                    if item['id'] > last_twitter_id:
                        p.set_last_twitter_id(item['id'])
                        contests.append(item)
        except Exception as e:
            err("[scan_for_contests] Search Error: %s" % e)

    out('bahh')

    scan_for_contests()
    update_queue()

    out('shamon')

    try:
        while 1:
            time.sleep(1)
    except KeyboardInterrupt as e:
        out("Closing...")

    out('rekt')

    exit(0)


def retweet_post(item, twitter, psql, followed, favourited):
    out("Retweeting...")
#    try:
#        twitter.api.PostRetweet(item['retweeted_status']['id'])
#    except Exception as e:
#        twitter.api.PostRetweet(item['id'])

    psql.add_contest(
        item['id'],
        item['text'],
        item['user']['screen_name'],
        't' if followed else 'f',
        't' if favourited else 'f'
    )
    psql.add_activity_log("Retweeted Post", item['id'])


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
#            twitter.api.DestroyFriendship(
#                screen_name=oldest_follower
#            )
            psql.add_activity_log(
                "Unfollowed %s" % oldest_follower,
                item['id']
            )

        # Follow the new guy
        try:
            new_follower = item['retweeted_status']['user']['screen_name']
#            twitter.api.CreateFriendship(
#                screen_name=new_follower
#            )
        except Exception as e:
            new_follower = item['user']['screen_name']
#            twitter.api.CreateFriendship(
#                screen_name=new_follower
#            )

        # Add follower to db
        psql.add_new_follower(new_follower)
        psql.add_activity_log('Followed %s' % new_follower, item['id'])
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
        favourited = True
#        try:
#            twitter.api.CreateFavorite(
#                id=item['retweeted_status']['user']['id']
#            )
#        except Exception as e:
#            twitter.api.CreateFavorite(
#                id=item['id']

        psql.add_activity_log('Favourited', item['id'])
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
