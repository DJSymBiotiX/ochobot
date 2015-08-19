#!/usr/bin/env python

from Util import (
    out,
    err
)
from sys import exit


class Twitter:


    def __init__(self, configfp):
        self.configs = self.__config_reader(configfp)
        self.api = self.__authenticate_to_twitter()


    def __authenticate_to_twitter(self):
        import twitter as twitter_api
        api = None
        try:
            api = twitter_api.Api(
                consumer_key        = self.configs['Twitter'][ 'ck'],
                consumer_secret     = self.configs['Twitter'][ 'cs'],
                access_token_key    = self.configs['Twitter']['atk'],
                access_token_secret = self.configs['Twitter']['ats']
            )
        except Exception as e:
            err("[Twitter] Authentication Error: %s" % e)
            exit(1)
        return api


    def __config_reader(self, configfp):
        import ConfigParser
        config = ConfigParser.ConfigParser()
        result = {}

        try:
            config.readfp(configfp)
        except Exception as e:
            err("[Twitter] Read Config Error: %s" % e)
            exit(1)

        # Read 'Twitter' Section
        result['Twitter'] = {
             'ck': config.get('Twitter', 'ck',  0),
             'cs': config.get('Twitter', 'cs',  0),
            'atk': config.get('Twitter', 'atk', 0),
            'ats': config.get('Twitter', 'ats', 0)
        }
        return result
