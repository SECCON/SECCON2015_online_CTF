#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import random
import cgi
import os
import base64
import hashlib

import pysqldb

def html(text):
	print "Content-Type: text/plain"
	print
	sys.stdout.write(text)
	sys.exit()

def success_upload(url):
	print "Content-Type: text/html"
	print
	print '<!DOCTYPE html>'
	print '<html>'
	print '<head>'
	print '<title>MD5 Collision Fight</title>'
	print '<meta http-equiv="refresh"content="5; url=' + url + '">'
	print '</head>'
	print '<body>Success!<br><a href="' + url + '">&lt;&lt;</a></body>'
	print '</html>'
	sys.exit()

def res_of_breakit(url, hashA, hashB):
	print "Content-Type: text/html"
	print
	print '<!DOCTYPE html>'
	print '<html>'
	print '<head>'
	print '<title>MD5 Collision Fight</title>'
	print '<meta http-equiv="refresh"content="5; url=' + url + '">'
	print '</head>'
	print '<body>'
	if hashA == hashB:
		print hashA + " == " + hashB + "<br>Success!<br>"
	else:
		print hashA + " != " + hashB + "<br>Failed...<br>"
	print '<br><a href="' + url + '">&lt;&lt;</a></body>'
	print '</html>'
	sys.exit()

def get_ip_address():
	if os.environ.has_key("REMOTE_ADDR"):
		return os.environ["REMOTE_ADDR"]
	html("ERR:get_ip_address")

def check_the_number(data):
	ch = "0123456789"
	for c in data:
		if not c in ch:
			return -1
	return 0

def check_the_teamname(data):
	ch  = "0123456789./ *"
	ch += "abcdefghijklmnopqrstuvwxyz"
	ch += "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
	for c in data:
		if not c in ch:
			return -1
	return 0

def get_MD5(data):
	return hashlib.md5(data).hexdigest()

def get_SHA512(data):
	return hashlib.sha512(data).hexdigest()

def hash_check(code1, code2):
	if get_MD5(code1) != get_MD5(code2):
		return 1
	if get_SHA512(code1) == get_SHA512(code2):
		return 1
	return 0

def read_uploaded_file(fi):
	if not fi.file:
		return None
	if not fi.filename:
		return None
	data = fi.file.read(256)
	while 1:
		chunk = fi.file.read(256)
		if not chunk:
			break
		data += chunk
	return data

def save_uploaded_file(data, upload_dir):
	fname = "11223344.bin"
	sfile = upload_dir + "11223344.bin"
	for i in range(10):
		fname = str(random.randint(10000000, 99999999)) + ".bin"
		sfile = os.path.join(upload_dir, fname)
		if os.path.isfile(sfile) == False:
			break
	fout = open(sfile, 'wb')
	fout.write(data)
	fout.close()
	return fname

def check_uploaded_file(E, D):
	if (1024 * 4) < len(E) or (1024 * 4) < len(D):
		html("ERR:((1024 * 4) < len(File)")
	if hash_check(E, D) == 1:
		html("ERR:" + get_MD5(E) + " != " + get_MD5(D))
	return (len(E), len(D), get_MD5(E))

def accept_uploaded_file(dbfile, upload_dir, FileA, FileB, Team):
	ip = get_ip_address()
	if ip == None:
		return -1
	# read files from HTTP
	E = read_uploaded_file(FileA)
	if E == None:
		return -1
	D = read_uploaded_file(FileB)
	if D == None:
		return -1
	# check the files
	finfo = check_uploaded_file(E, D)
	# save files which is same MD5 each other
	dirpath = os.path.join(upload_dir, ip)
	if os.path.isdir(dirpath) == False:
		os.mkdir(dirpath)
	fAname = save_uploaded_file(E, dirpath)
	fBname = save_uploaded_file(D, dirpath)
	# TeamName
	TmName = base64.b64encode(Team)
	# update DB
	# finfo = [FileA size, FileB size, MD5]
	h = pysqldb.datactrl(dbfile)
	data = [
		0, #id
		finfo[0], #codesize(A)
		finfo[1], #codesize(B)
		finfo[2], #MD5
		ip,       #ip
		TmName,   #TeamName
		fAname,   #name of FileA
		fBname    #name of FileB
	]
	h.put_data(data)
	return 0

def post_files(dbfile, form, uppath, topurl):
	# check form
	if not form.has_key("FileA") or not form.has_key("FileB") or not form.has_key("Team"):
		html("ERR:no_param")
	# client post files
	if accept_uploaded_file(dbfile, uppath, form["FileA"], form["FileB"], form["Team"].value) == -1:
		html("ERR:unknown(post_files)")
	success_upload(topurl)

def get_ranking(dbfile, form):
	# get offset
	st = 0
	if form.has_key("n"):
		if check_the_number(form["n"].value) == -1:
			st = 0
		else:
			try:
				st = int(form["n"].value)
				if st < 0:
					st = 0
			except:
				st = 0
	# get size
	sz = 10
	if form.has_key("m"):
		if check_the_number(form["m"].value) == -1:
			sz = 10
		else:
			try:
				sz = int(form["m"].value)
				if sz < 0:
					sz = 10
			except:
				sz = 10
	# read DB
	h = pysqldb.datactrl(dbfile)
	sql  = ""
	sql += "order by status asc, (codesizeA+codesizeB) asc, id asc limit "
	sql += " " + str(st) + ", " + str(sz)
	datalist = h.get_data(sql)
	r = str(h.get_count())
	# write data
	for i in range(len(datalist)):
		r += "\x0a"
		v = datalist[i]
		# v[0]: codeid = idenfity of code
		# v[1]: csizeA = code size(A)
		# v[2]: csizeB = code size(B)
		# v[3]: MD5    = MD5 hash
		# v[4]: ip     = ip address
		# v[5]: Team   = team name
		# v[6]: FileA  = FileA name
		# v[7]: FileB  = FileB name
		# v[8]: status = count of break team
		# v[9]: bips   = break team list
		r += "%08d@%d@%d@%s@%s@%d" % (v[0], v[1], v[2], v[3], v[5], v[8])
	html(r)

def break_it(dbfile, form, uppath, topurl):
	ip = get_ip_address()
	if not form.has_key("FileC"):
		html("ERR:has_key(FileC)")
	F = read_uploaded_file(form["FileC"])
	if F == None:
		html("ERR:unknown3(break_it)")
	if (1024 * 4) < len(F):
		html("ERR:((1024 * 4) < len(File)")
	if not form.has_key("n"):
		html("ERR:has_key(n)")
	if check_the_number(form["n"].value) == -1:
		html("ERR:unknown0(break_it)")
	# read DB
	cid = 0
	try:
		cid = int(form["n"].value)
	except:
		html("ERR:unknown2(break_it)")
	h = pysqldb.datactrl(dbfile)
	datalist = h.get_data("where id='" + str(cid) + "'")
	if len(datalist) != 1:
		html("ERR:unknown1(break_it)")
	# v[0]: codeid = idenfity of code
	# v[1]: csizeA = code size(A)
	# v[2]: csizeB = code size(B)
	# v[3]: MD5    = MD5 hash
	# v[4]: ip     = ip address
	# v[5]: Team   = team name
	# v[6]: FileA  = FileA name
	# v[7]: FileB  = FileB name
	# v[8]: status = count of break team
	# v[9]: bips   = break team list
	uMD5 = get_MD5(F)
	sMD5 = datalist[0][3]
	if uMD5 == sMD5:
		h.broken(cid, ip)
	res_of_breakit(topurl, uMD5, sMD5)

def get_default():
	html("Start where you are. Use what you have. Do what you can.")

def main():
	# dir/file path
	topurl = "./"
	dbfile = "db/files.db"
	uppath = "uploadfiles/"
	# get form data
	form = cgi.FieldStorage()
	# s is status code (=Necessary)
	if form.has_key("s") and form["s"].value != "":
		# post script
		if form["s"].value == "post_files":
			post_files(dbfile, form, uppath, topurl)
		# get ranking
		if form["s"].value == "get_ranking":
			get_ranking(dbfile, form)
		# try break_it
		if form["s"].value == "break_it":
			break_it(dbfile, form, uppath, topurl)
	get_default()

if __name__ == "__main__":
	main()
