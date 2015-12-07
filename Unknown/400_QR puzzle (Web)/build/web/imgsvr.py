#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# QR puzzle image server
#
# For the SECCON CTF 2015 online qualifications
# Title : QR puzzle (Web)
# Genre : Unknown
# Points: 400
# Author: @shiracamus
#
# Need to install packages:
#   sudo pip install bottle
#   sudo pip install paste

from bottle import route, run, abort, static_file, get, post, request, redirect, HTTPResponse
from datetime import datetime
import sys

#############################################################################
# utility functions
#############################################################################

def unscramble(path):
    xor1 = ord(path[:2].decode('hex'))
    xor2 = ord(path[-2:].decode('hex'))
    data = map(ord, path[2:-2].decode('hex'))
    for i in range(1,len(data),2):
	data[i] ^= xor1
    for i in range(0,len(data),2):
	data[i] ^= xor2
    data = ''.join(map(chr, data))
    hexkey = data[:-5].encode('hex')
    number = int(data[-5].encode('hex'), 16)
    limit = int(data[-4:].encode('hex'), 16)
    return hexkey, number, limit

def now():
    return int(mktime(datetime.now().timetuple()))

#############################################################################
# URL path handlers
#############################################################################

@route('/img/<path>')
def imageurl(path):
    if path.endswith('>'):
        path = path[:-1]
    if path[-4:] != '.png':
	abort(404, 'Not Found: /img/' + path)
    imagekey, number, limit = unscramble(path[:-4])
    if imagekey not in images or number > GOAL:
	abort(404, 'Not Found: /img/' + path)
    if now() > limit:
	return static_file('QR0000-00.png', root='./img')
    image = images[imagekey]
    return static_file(image.name, root='./img')

#############################################################################

if __name__ == '__main__':
    argc = len(sys.argv)
    if (argc < 2):
      print "Usage: imgsvr.py <port>"
      quit()
    port = sys.argv[1]
    run(host='0.0.0.0', port=port, server='paste', debug=False, reloader=True, quiet=True)
