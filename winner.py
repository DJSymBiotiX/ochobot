#!/usr/bin/env python

from libocho.Twitter import Twitter
from libocho.PSQL import PSQL
from libocho.Util import (
    out,
    err,
    read_json_config
)
from sys import exit
from threading import (
    Timer,
    Lock
)
from time import sleep

import random

# Globals
debug = False


def main():
    args = parse_args()

    try:
        config = read_json_config(args.configPath)
        t = Twitter(config['twitter'])
        p = PSQL(config['psql'])
        s = config['settings']
    except Exception as e:
        err(e)
        exit(1)

    # Set up debug
    global debug
    debug = args.debug

    # Contests Queue
    contests = []

    # Create Mutex Lock
    mutex = Lock()

    def update_queue():
        time = get_fuzzed_time(s['retweet']['base'], s['retweet']['fuzz'])
        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)
        out("update_queue random time: %sh%sm" % (int(hours), int(minutes)))

        # Setup and start the threading
        u = Timer(time, update_queue)
        u.daemon = True
        u.start()

        mutex.acquire()
        try:
            if len(contests) > 0:
                contest = contests[0]
                out("Contest: %s" % contest['text'])

                followed = check_for_follow_request(contest, t, p, s)
                favourited = check_for_favourite_request(contest, t, p, s)
                retweet_post(contest, t, p, s, followed, favourited)

                contests.pop(0)
        finally:
            mutex.release()

    def scan_for_contests():
        time = get_fuzzed_time(s['search']['base'], s['search']['fuzz'])
        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)
        out("scan_for_contests random time: %sh%sm" % (int(hours), int(minutes)))

        # Setup and start the threading
        v = Timer(time, scan_for_contests)
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


def get_fuzzed_time(base, fuzz):
    base_time = 60.0 * base
    fuzz_time = 60.0 * random.randrange(-1 * fuzz, fuzz)

    return base_time + fuzz_time


def retweet_post(item, twitter, psql, settings, followed, favourited):
    out("Retweeting...")

    # Check if we have already retweeted this post
    retweeted = False
    try:
        tweet_id = item['retweeted_status']['id']
        if not psql.check_contest(tweet_id):
            retweeted = True
            if not debug:
                twitter.api.PostRetweet(tweet_id)
    except Exception as e:
        retweeted = False
        try:
            tweet_id = item['id']
            if not psql.check_contest(tweet_id):
                retweeted = True
                if not debug:
                    twitter.api.PostRetweet(tweet_id)
        except Exception as e:
            retweeted = False

    if retweeted:
        if not debug:
            psql.add_contest(
                tweet_id,
                item['text'],
                item['user']['screen_name'],
                followed,
                favourited
            )


def check_for_follow_request(item, twitter, psql, settings):
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
        if follower_count >= settings['max_followers']:
            oldest_follower = psql.get_oldest_follower()
            out("Too many followers: Unfollowing %s" % oldest_follower)

            # Unfollow that nerd
            if not debug:
                twitter.api.DestroyFriendship(
                    screen_name=oldest_follower
                )
                psql.unfollow_user(oldest_follower)

        if not debug:
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


def check_for_favourite_request(item, twitter, psql, settings):
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
            if not debug:
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
    parser.add_argument(
        '-d', '--debug',
        action="store_true",
        help="do not retweet, favourite, or follow when on"
    )

    return parser.parse_args()


if __name__ == "__main__":
    main()
