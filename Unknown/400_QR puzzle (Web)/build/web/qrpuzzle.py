#!/usr/bin/env python
# -*- coding:utf-8 -*-
#
# QR puzzle main server script
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
#   pip install wsgi-request-logger

from bottle import route, run, abort, static_file, get, post, request, redirect, HTTPResponse
import random
from datetime import datetime
from time import sleep, mktime
from sys import stdout
from hashlib import md5

GOAL = 50
TIMEOUT = 60 #seconds

#############################################################################
# result functions
#############################################################################

def log(message):
    stdout.write( datetime.now().strftime('%Y/%m/%d %H:%H:%S')
                + ' ' + repr(request.remote_addr) + ' '
                + message
                + '\n' )
    stdout.flush()

def wrong():
    sleep(1)
    log('wrong')
    return 'Wrong'

def timeout():
    sleep(1)
    log('timeout')
    return 'Too late'

def show_flag():
    log('flag')
    return '''Congraturations!!
<br>
The flag is SECCON{U_R_4_6R347_PR06R4MM3R!}
'''

#############################################################################
# utility functions
#############################################################################

def scramble(hexkey, number, limit):
    xor1 = random.randint(0, 0xff)
    xor2 = random.randint(0, 0xff)
    data = map(ord, (hexkey + '%02x' % number + '%08x' % limit).decode('hex'))
    for i in range(1,len(data),2):
	data[i] ^= xor1
    for i in range(0,len(data),2):
	data[i] ^= xor2
    data = ''.join(map(chr, data)).encode('hex')
    return '%02x' % xor1 + data + '%02x' % xor2

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
# puzzle data
#############################################################################

puzzles = {}
images = {}
tiles = tuple('%d%d' % (y, x)
              for y in (1,2,3,4)
              for x in (1,2,3,4))

class QRimage(object):
    def __init__(self, qrname, x, y):
        self.name = '%s-%d%d.png' % (qrname, y, x)
        self.x = x
        self.y = y
        self.key = md5(self.name).hexdigest()

    def __repr__(self):
        return 'QRimage(%s, %d, %d)' % (repr(self.name[:self.name.index('-')]), self.x, self.y)

class QRpuzzle(object):
    def __init__(self, name, text):
        self.name = name
        self.text = text
        self.key = md5('SECCON2015-' + name).hexdigest()
        self.images = { '%d%d'%(y,x) : QRimage(name, x, y)
                        for y in (1,2,3,4)
                        for x in (1,2,3,4) }
        self.images['00'] = QRimage(name, 0, 0)

    def __repr__(self):
        return 'QRpuzzle(%s, %s)' % (repr(self.name), repr(self.text))

def load_catalog():
    with open('../catalog.txt') as f:
        for line in f:
            puzzlename, text = line.split()
            puzzle = QRpuzzle(puzzlename, text)
            if puzzle.key in puzzles:
                print "ERROR: Conflict a QR name"
                sys.exit(1)
            puzzles[puzzle.key] = puzzle
            for image in puzzle.images.values():
                if image.key in images:
                    print "ERROR: Conflict a image name"
                    sys.exit(1)
                images[image.key] = image

#############################################################################
# make puzzle
#############################################################################

class Level(object):
    def __init__(self, name, spaces):
        self.name = name
        self.spaces = spaces

levels = ( Level('Easy', ['44']),
           Level('Medium', ['12', '13', '21', '24', '31', '34', '42', '43']),
           Level('MediumHard', [ '22', '23', '32', '33']),
           Level('Hard', ['11', '14', '41']),
           Level('Random', tiles) )

class Slider(object):
    def __init__(self, name, space=tiles[-1]):
        self.tiles = dict(zip(tiles, tiles))
        self.space = space

    def slide(self):
        space = int(self.space)
        neighbors = map(str, (space+1, space-1, space+10, space-10))
        neighbors = [ neighbor
                      for neighbor in neighbors
                      if neighbor in tiles ]
        neighbor = random.choice(neighbors)
        space = self.tiles[self.space]
        self.tiles[self.space] = self.tiles[neighbor]
        self.tiles[neighbor] = space
        self.space = neighbor

    def shuffle(self, times):
        for i in xrange(times):
            self.slide()

    def get_tile(self, x, y):
        pos = '%d%d' % (y, x)
        if pos == self.space:
            return '00'
        return self.tiles[pos]

def show_puzzle(number):
    sleep(1)
    puzzlekey = random.choice(puzzles.keys())
    puzzle = puzzles[puzzlekey]
    #print puzzle.name, puzzle.text
    level = levels[(number - 1) * len(levels) / GOAL]
    space = random.choice(level.spaces)
    slider = Slider(puzzle.name, space)
    shuffle_times = (1,2,3,5,10,20,30,40,50,100)[(number - 1) % 10]
    slider.shuffle(shuffle_times)
    limit = now() + TIMEOUT
    path = scramble(puzzlekey, number, limit)
    imagehtml = ''
    for y in (1,2,3,4):
        for x in (1,2,3,4):
            tile = slider.get_tile(x, y)
            image = puzzle.images[tile]
            imagepath = scramble(image.key, number, limit)
            # imagehtml += "<img src='img/%s.png>' name='%d%d' onclick=clicked(this)>" % (imagepath, y, x)
            imagehtml += "<img src='http://puzzle.quals.seccon.jp:100%d%d/img/%s.png>' name='%d%d' onclick=clicked(this)>" % (y, x, imagepath, y, x)
        imagehtml += '<br>'
    return '''<html>
<head>
<title>Decode the QR code</title>
<script type=text/javascript>
<!--
var space = %s;

function clicked(img) {
    var number = parseInt(img.name);
    var neighbors = [ number+1, number-1, number+10, number-10 ];
    for (var i = 0; i < neighbors.length; i++) {
        var neighbor = neighbors[i];
        if (neighbor != space)
            continue;
        var images = document.images;
        for (var index = 0; index < images.length; index++) {
            var target = images[index];
            if (target.name != String(neighbor))
                continue;
            var src = img.src;
            img.src = target.src;
            target.src = src;
            space = number;
            break;
        }
    }
}
// -->
</script>
</head>
<body>
No. %d of %d
<br>
Level: %s
<p/>
%s
<p/>
<form action="%s" method="POST">
Decode: <input type="text" name="text" size="33">
<input type="submit" value="Submit">
</form>
</body>
</html>
''' % (slider.space, number, GOAL, level.name, imagehtml, path)

#############################################################################
# URL path handlers
#############################################################################

@route('/')
def home():
    return "The server works. Specify the path of the target page."

@route('/slidepuzzle')
def game():
    return show_puzzle(1)

@route('/robots.txt')
@route('/favicon.ico')
def staticurl():
    return static_file(request.urlparts.path, root='./static')

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

#@get('/<path:re:[0-9a-f]{46}>')
@post('/<path:re:[0-9a-f]{46}>')
def judge(path):
    puzzlekey, number, limit = unscramble(path)
    if puzzlekey not in puzzles or number > GOAL:
	abort(404, 'Not Found: ' + path)
    if now() > limit:
	return timeout()
    puzzle = puzzles[puzzlekey]
    #text = request.query.text
    text = request.forms.get('text')
    if text != puzzle.text:
        return wrong()
    if number == GOAL:
        return show_flag()
    return show_puzzle(number + 1)

#############################################################################

if __name__ == '__main__':
    load_catalog()
    run(host='0.0.0.0', port=42213, server='paste', debug=False, reloader=True, quiet=True)
