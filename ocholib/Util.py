#!/usr/bin/env python

from sys import (
    stdout,
    stderr
)


def out(msg):
    print >> stdout, msg


def err(msg):
    print >> stderr, msg
