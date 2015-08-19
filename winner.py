#!/usr/bin/env python

from libocho.Twitter import Twitter
from libocho.PSQL import PSQL
from libocho.Util import (
    out,
    err
)
from sys import exit

def main():
    args = parse_args()

    # t = Twitter API, p = PSQL Class (Not really used), s = PSQL Session
    t = Twitter(args.configPath)
    p = PSQL(args.configPath)
    s = p.session

    contests = []

    contests += scan_for_contests(t, s)

    exit(0)

def scan_for_contests(twitter, session):
    out("Scanning For Contests...")
    last_twitter_id = session.execute(
        "SELECT last_twitter_id FROM info"
    ).fetchone()[0]
    items = []

    try:
        results = twitter.api.GetSearch(
            term="RT to win",
            since_id=last_twitter_id
        )

        for status in results:
            item = status.AsDict()
            if item['retweet_count'] > 0:
                if item['id'] > last_twitter_id:
                        # Update last_twitter_id
                        session.execute(
                            "UPDATE info SET last_twitter_id = '%s'" % (
                                item['id']
                            )
                        )
                        session.commit()
                        items.append(item)
                        out(item)
    except Exception as e:
        err("[scan_for_contests] Search Error: %s" % e)
    return items




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
