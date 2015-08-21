#!/usr/bin/env python

from sys import (
    stdout,
    stderr
)

from datetime import datetime

def read_json_config(config_path):
    try:
        import json
    except ImportError:
        import simplejson as json

    try:
        with open(config_path, 'rb') as f:
            data = json.load(f)
            return data
    except Exception as e:
        raise e
    return {}


def out(msg):
    try:
        print >> stdout, "%s: %s" % (datetime.now(), msg)
    except Exception as e:
        err("[out] Could Not Print: %s" % e)


def err(msg):
    try:
        print >> stderr, msg
    except Exception as e:
        print >> stderr, ("[err] Coult Not Print: %s" % e)
