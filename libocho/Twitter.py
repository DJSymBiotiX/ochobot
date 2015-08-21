#!/usr/bin/env python


class Twitter:
    def __init__(self, config):
        import twitter as twitter_api
        try:
            self.api = twitter_api.Api(
                consumer_key        = config[       'consumer_key'],
                consumer_secret     = config[    'consumer_secret'],
                access_token_key    = config[   'access_token_key'],
                access_token_secret = config['access_token_secret']
            )
        except Exception as e:
            raise ('[Twitter.py] %s' % e)
