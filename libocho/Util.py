#!/usr/bin/env python

from sys import (
    stdout,
    stderr
)

from datetime import datetime


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
