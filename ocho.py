#!/usr/bin/env python

from ocholib.Twitter import Twitter
from ocholib.Util import (
    out,
    err
)
from sys import exit

def main():
    args = parse_args()

    out("Checking For Ochos....")

    limit = 1

    t = Twitter(args.configPath)

    try:
        eight = t.api.GetSearch(
            term='Eight',
            count=10,
            result_type='recent',
            lang='en'
        )
        ocho = t.api.GetSearch(
            term='8',
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
    for x in ocho:
        text = x.AsDict()['text']
        blacklist = ['0', '1', '2', '3', '4', '5', '6', '7', '9']
        if filter_search(text, '8', blacklist) is not None:
            matches.append(x)

    count = 0
    for x in matches:
        text = x.AsDict()['text']
        status_id = x.id
        user_id = x.user.AsDict()['id']
        screen_name = x.user.AsDict()['screen_name']

        out("That's Ocho!")
        out(text)

        try:
            t.api.PostUpdate(
                "@%s That's Ocho!" % screen_name,
                in_reply_to_status_id=status_id
            )
        except Exception, e:
            err("PostUpdate Exception: %s" % e)
        out('')
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
        description="That's Ocho!",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        'configPath',
        type=argparse.FileType('rb'),
        help="Path to config file"
    )

    return parser.parse_args()


if __name__ == "__main__":
    main()
