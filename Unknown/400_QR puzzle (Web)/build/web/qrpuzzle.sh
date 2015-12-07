#!/bin/sh

# Run QR puzzle server scripts
# Before run, need to run make_images.py on the parent directory

# For the SECCON CTF 2015 online qualifications
# Title : QR puzzle (Web)
# Genre : Unknown
# Points: 400
# Author: @shiracamus

nohup python2.7 imgsvr.py 10011 >/dev/null 2>/dev/null &
nohup python2.7 imgsvr.py 10012 >/dev/null 2>/dev/null &
nohup python2.7 imgsvr.py 10013 >/dev/null 2>/dev/null &
nohup python2.7 imgsvr.py 10014 >/dev/null 2>/dev/null &

nohup python2.7 imgsvr.py 10021 >/dev/null 2>/dev/null &
nohup python2.7 imgsvr.py 10022 >/dev/null 2>/dev/null &
nohup python2.7 imgsvr.py 10023 >/dev/null 2>/dev/null &
nohup python2.7 imgsvr.py 10024 >/dev/null 2>/dev/null &

nohup python2.7 imgsvr.py 10031 >/dev/null 2>/dev/null &
nohup python2.7 imgsvr.py 10032 >/dev/null 2>/dev/null &
nohup python2.7 imgsvr.py 10033 >/dev/null 2>/dev/null &
nohup python2.7 imgsvr.py 10034 >/dev/null 2>/dev/null &

nohup python2.7 imgsvr.py 10041 >/dev/null 2>/dev/null &
nohup python2.7 imgsvr.py 10042 >/dev/null 2>/dev/null &
nohup python2.7 imgsvr.py 10043 >/dev/null 2>/dev/null &
nohup python2.7 imgsvr.py 10044 >/dev/null 2>/dev/null &

nohup python2.7 qrpuzzle.py &
