#!/usr/bin/env python

from sys import (
    stdout,
    stderr
)


def out(msg):
    try:
        print >> stdout, msg
    except Exception as e:
        err("[out] Could Not Print: %s" % e)


def err(msg):
    try:
        print >> stderr, msg
    except Exception as e:
        print >> stderr, ("[err] Coult Not Print: %s" % e)
