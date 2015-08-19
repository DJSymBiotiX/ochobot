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

    out("Checking For Ochos....")

    limit = 1

    #t = Twitter(args.configPath)
    p = PSQL(args.configPath)
    session = p.session

    x = session.execute('SELECT * FROM followers');
    for row in x:
        print row

    exit(0)
    try:
        eight = t.api.GetSearch(
            term='Eight',
            count=10,
            result_type='recent',
            lang='en'
        )
    except Exception as e:
        err("[Main] Search Failure: %s" % e)
        eight = []
        ocho = []

    matches = []
    for x in eight:
        text = x.AsDict()['text']
        blacklist = [
            'zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven',
            'nine'
        ]
        if filter_search(text, 'eight', blacklist) is not None:
            matches.append(x)

    count = 0
    for x in matches:
        out(x.AsDict())
        out('\n\n\n')
        count += 1
        if count == limit:
            exit(0)

    exit(0)

def filter_search(text, term, blacklist):
    idx = text.lower().find(term.lower())
    if idx == -1:
        return None

    # Ignore retweets
    if text.lower()[0:2] == 'rt':
        return None

    # Ignore if has blacklist text
    for item in blacklist:
        if item.lower() in text.lower():
            return None

    whitelist = [' ', '.', '-', '\n']
    before = ''
    after = ''

    len8 = len(term)
    if idx + len8 >= len(text):
        after = ' '
    else:
        after = text[idx + len8]

    if idx - 1 <= 0:
        before = ' '
    else:
        before = text[idx - 1]

    if before in whitelist and after in whitelist:
        return "That's Ocho!"
    return None

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
