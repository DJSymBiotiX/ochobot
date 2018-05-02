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

    usedpath = 'whitehout_posted.txt'

    out('Checking For #WPGWhitehout....')

    limit = 1

    try:
        config = read_json_config(args.configPath)
        t = Twitter(config['twitter'])
    except Exception as e:
        err(e)
        exit(1)

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
                    count=10,
                    result_type='recent',
                    lang='en'
                )
            except Exception as e:
                err('[Main] Search Failure: %s' % e)
                wpgwhitehout = []

            matches = []
            for x in wpgwhitehout:
                text = x.AsDict()['text']
                if text.lower()[0:2] != 'rt':
                    matches.append(x)

            used_ids = []
            with open(usedpath, 'r') as f:
                for line in f:
                    used_ids.append(int(line.strip()))

            count = 0
            for x in matches:
                text = x.AsDict()['text']
                status_id = x.id
                screen_name = x.user.AsDict()['screen_name']

                try:
                    if status_id in used_ids:
                        continue
                    out("That's WPGWhitehout")
                    out(text)
                    if dry_run:
                        out('@%s I think you mean #WPGWhiteout' % screen_name)
                    else:
                        t.api.PostUpdate(
                            '@%s I think you mean #WPGWhiteout' % screen_name,
                            in_reply_to_status_id=status_id
                        )
                        # Write used id to file
                        with open(usedpath, 'a') as f:
                            f.write('%s\n' % status_id)

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
