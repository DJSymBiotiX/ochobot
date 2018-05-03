#!/usr/bin/env python

from libocho.Twitter import Twitter
from libocho.Util import (
    out,
    err,
    read_json_config
)
from threading import (
    Timer,
    Lock
)
from sys import exit
from time import sleep

import random


def main():
    args = parse_args()
    dry_run = args.dry_run

    usedpath = 'whitehout_lastused.txt'

    out('Checking For #WPGWhitehout....')

    limit = 1

    try:
        config = read_json_config(args.configPath)
        t = Twitter(config['twitter'])
    except Exception as e:
        err(e)
        exit(1)

    phrases = [
        'I think you mean #WPGWhiteout',
        "Are you sure it's #WPGWhitehout and not #WPGWhiteout?",
        (
            'Looks like an "h" snuck its way in that hashtag. '
            'I think you mean #WPGWhiteout'
        ),
        'Let me just fix that up for you :) #WPGWhiteout not #WPGWhitehout',
        "What's a Hout? Did you mean #WPGWhiteout?",
        (
            "There's an H in Nashville but not one in Winnipeg, "
            "so don't use it in the hashtag. #WPGWhiteout"
        ),
        '#WPGWhitehout is wrong. #WPGWhiteout is right',
        (
            '#WPGWhitehout supports the Houts, #WPGWhiteout supports the '
            'Jets. Notice the logo!'
        )
    ]

    # Create Mutex Lock
    mutex = Lock()

    def check_for_whitehout():
        time = get_fuzzed_time(5, 3)
        minutes, seconds = divmod(time, 60)
        hours, minutes = divmod(minutes, 60)
        out('random time: %sh%sm%ss' % (
            int(hours), int(minutes), int(seconds)
        ))

        # Setup and start the threading
        x = Timer(time, check_for_whitehout)
        x.daemon = True
        x.start()

        mutex.acquire()
        try:
            try:
                wpgwhitehout = t.api.GetSearch(
                    term='#WPGWhitehout',
                    count=30,
                    result_type='recent',
                    lang='en'
                )
            except Exception as e:
                err('[Main] Search Failure: %s' % e)
                wpgwhitehout = []

            matches = []
            for x in wpgwhitehout:
                text = x.AsDict()['text']
                if (
                    text.lower()[0:2] != 'rt' and
                    x.user.screen_name != 'wpgwhitehout'
                ):
                    matches.append(x)

            used_id = -1
            with open(usedpath, 'r') as f:
                # There should only be one line
                used_id = int(f.read().strip())

            count = 0
            for x in matches:
                text = x.AsDict()['text']
                status_id = x.id
                screen_name = x.user.AsDict()['screen_name']

                try:
                    print status_id
                    print used_id
                    if status_id <= used_id:
                        continue
                    out(text)
                    response = '@%s %s' % (screen_name, random.choice(phrases))
                    out('Response: %s' % response)
                    if not dry_run:
                        t.api.PostUpdate(
                            response,
                            in_reply_to_status_id=status_id
                        )
                        # Write used id to file
                        with open(usedpath, 'w') as f:
                            f.write('%s' % status_id)

                except Exception, e:
                    err('PostUpdate Exception: %s' % e)

                out('')
                count += 1
                if count == limit:
                    break
        finally:
            mutex.release()

    check_for_whitehout()

    try:
        while 1:
            sleep(1)
    except KeyboardInterrupt as e:
        out('Closing...')

    exit(0)


def get_fuzzed_time(base, fuzz):
    base_time = 60.0 * base
    fuzz_time = random.randrange(-1 * int((60 * fuzz)), int((60 * fuzz)))
    return base_time + fuzz_time


def parse_args():
    import argparse
    parser = argparse.ArgumentParser(
        description="That's Ocho!",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        'configPath',
        type=str,
        help='Path to config file'
    )

    parser.add_argument(
        '-d', '--dry_run',
        action='store_true',
        help="dry run, don't post to twitter"
    )

    return parser.parse_args()


if __name__ == '__main__':
    main()
