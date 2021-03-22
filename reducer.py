#!/usr/bin/python
#encoding: utf-8

# output all output of mapper as it is.

import os
import sys
import time
import string
import datetime

def stats(fp = sys.stdin):
    for line in fp:
        line = line.strip()
        print line

if __name__ == "__main__":
    stats()