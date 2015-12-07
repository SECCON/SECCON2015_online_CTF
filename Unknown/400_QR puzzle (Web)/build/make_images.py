#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Create QR code image files.
#
# For the SECCON CTF 2015 online qualifications
# Title : QR puzzle (Web)
# Genre : Unknown
# Points: 400
# Author: @shiracamus
#
# Need to install packages:
#   sudo apt-get install python-imaging
#   sudo apt-get install python-qrcode
#   sudo apt-get install python-qrtools

import os
import shutil
import colorsys
import Image, ImageDraw
import qrcode
from random import random, randint, choice
from hashlib import md5
import qrtools

NUM = 500
TEXT_LENGTH = 32
TEXT_CHARS = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
DIVIDE = 4  # 4 means 4x4
DIR = './web/img'

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

qr = qrtools.QR()

def make_qrcode(number, text):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=5,
        border=3)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image()
    return img

def crop_image(img, x, y):
    width, height = img.size
    size = width / DIVIDE
    return img.crop((size * x, size * y, size * (x + 1), size * (y + 1)))

def save_image(number):
    name = 'QR%04d' % number
    imgname = '%s/%s.png' % (DIR, name))
    while True:
        text = ''.join(choice(TEXT_CHARS) for i in range(TEXT_LENGTH))
        img = make_qrcode(number, text)
        if img.size != (215, 215):
            continue
        # check to decode without the lower right tile
        size = img.size[0] / DIVIDE
        x = y = (DIVIDE - 1) * size
        empty = img.crop((0, 0, size * DIVIDE, size * DIVIDE))
        draw = ImageDraw.Draw(empty)
        draw.rectangle((x, y, x + size, y + size), fill=0, outline='rgb(0,0,0)')
        empty.save(imgname)
        qr.data = ''
        qr.decode(imgname)
        if qr.data == text:
            break
    img.save(imgname)
    for y in range(DIVIDE):
        for x in range(DIVIDE):
            part = crop_image(img, x, y)
            part.save('%s/%s-%d%d.png' % (DIR, name, y + 1, x + 1))
    width, height = img.size
    space = Image.new('RGB', (width / DIVIDE, height / DIVIDE), BLACK)
    space.save('%s/%s-00.png' % (DIR, name))
    return name, text

if __name__ == '__main__':
    try:
        shutil.rmtree('./web/img')
    except OSError:
        pass
    os.makedirs('./web/img')

    with open('catalog.txt', 'w') as catalog:
        for i in range(NUM):
            if i % 100 == 0: print i
            name, text = save_image(i)
            catalog.write('%s %s\n' % (name, text))
