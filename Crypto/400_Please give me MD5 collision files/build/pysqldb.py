#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import sqlite3

def tounicode(utf_text):
	return unicode(utf_text, 'utf-8')

def toutf8(uni_text):
	return uni_text.encode('utf-8')

class datactrl:
	# START
	def __init__(self, dbname):
		self.db = sqlite3.connect(dbname)
		self.cr = self.db.cursor()
	# create table
	def create_table(self):
		sql  = u""
		sql += u"create table files ("
		sql += u"id integer primary key autoincrement,"
		sql += u"codesizeA integer,"
		sql += u"codesizeB integer,"
		sql += u"MD5 text,"
		sql += u"ip text,"
		sql += u"TeamName text,"
		sql += u"FileA text,"
		sql += u"FileB text,"
		sql += u"status integer,"
		sql += u"bips text);"
		self.cr.execute(sql)
		self.db.commit()
	# write new data
	def put_data(self, data):
		(cid, csA, csB, ha, ip, tn, A, B) = data
		sql  = u""
		sql += u"insert into files ("
		sql += u"codesizeA, codesizeB, MD5, ip, TeamName, FileA, FileB, status, bips) values ("
		sql += u"" + tounicode(str(csA)) + u","
		sql += u"" + tounicode(str(csB)) + u","
		sql += u"'" + tounicode(ha) + u"',"
		sql += u"'" + tounicode(ip) + u"',"
		sql += u"'" + tounicode(tn) + u"',"
		sql += u"'" + tounicode(A)  + u"',"
		sql += u"'" + tounicode(B)  + u"',"
		sql += u"'0',"
		sql += u"'');"
		self.cr.execute(sql)
		self.db.commit()
	# read data
	def get_data(self, addi):
		if addi == None:
			self.cr.execute(u"select * from files;")
		else:
			self.cr.execute(u"select * from files " + tounicode(addi) + u";")
		datalist = []
		for r in self.cr.fetchall():
			x = [
				r[0],         #id
				r[1],         #codesizeA
				r[2],         #codesizeB
				toutf8(r[3]), #MD5
				toutf8(r[4]), #ip
				toutf8(r[5]), #TeamName
				toutf8(r[6]), #name of FileA
				toutf8(r[7]), #name of FileB
				r[8],         #status
				toutf8(r[9])  #ip list of break it
			]
			datalist.append(x)
		return datalist
	# break it
	def broken(self, cid, ip):
		datalist = self.get_data("where id='" + str(cid) + "'")
		if len(datalist) < 1:
			return -1
		n = datalist[0][8] + 1 #status += 1
		bips = datalist[0][9]  #iplist.add(ip)
		ipli = bips.split(',')
		if ip in ipli:
			return -1
		if 1 < n:
			bips += "," + ip
		else:
			bips = ip
		sql  = u""
		sql += u"update files set status='" + str(n) + u"' where id='"
		sql += tounicode(str(cid)) + u"';"
		self.cr.execute(sql)
		self.db.commit()
		sql  = u""
		sql += u"update files set bips='" + tounicode(bips) + u"' where id='"
		sql += tounicode(str(cid)) + u"';"
		self.cr.execute(sql)
		self.db.commit()
		return 0
	# get count of data in table
	def get_count(self):
		self.cr.execute(u'select count(id) from files;')
		datalist = []
		for r in self.cr.fetchall():
			datalist.append(r)
		return datalist[0][0]
	# FINISH
	def __del__(self):
		self.cr.close()
		self.db.close()

#----------------------------------------------
# TEST CODE
#----------------------------------------------
def main():
	handle = datactrl(sys.argv[1])
	dbmode = sys.argv[2]
	# create
	if dbmode == "create":
		handle.create_table()
		print "create success"
	# write
	elif dbmode == "write":
		if len(sys.argv) < 7:
			print "err: write need csizeA,csizeB,MD5,TeamName in argv[3],argv[4],argv[5],argv[6]"
			sys.exit()
		csizeA  = int(sys.argv[3])
		csizeB  = int(sys.argv[4])
		h_MD5   = sys.argv[5]
		TeamName= sys.argv[6]
		data = [0, csizeA, csizeB, h_MD5, "127.0.0.1", TeamName, "00000000", "99999999"]
		handle.put_data(data)
		print "write success"
	# read
	elif dbmode == "read":
		addi = None
		if len(sys.argv) == 5:
			li1 = sys.argv[3] # limit start
			li2 = sys.argv[4] # limit size
			addi = "order by status asc, (codesizeA+codesizeB) asc, id asc limit " + li1 + ", " + li2
		data = handle.get_data(addi)
		for li in data:
			print li
		print "read success"
	# broken
	elif dbmode == "broken":
		if len(sys.argv) < 5:
			print "err: broken need ID,IP in argv[3],argv[4]"
			sys.exit()
		cid = sys.argv[3]
		handle.broken(int(cid), sys.argv[4])
		print "broken success"
	elif dbmode == "count":
		print "Count: " + str(handle.get_count())

if __name__ == "__main__":
	if len(sys.argv) < 3:
		print ">this.py [dbfile] [create/read/write/broken]"
		print "  create"
		print "  read [start] [size]"
		print "  write [fileA size] [fileB size] [MD5] [TeamName]"
		print "  broken [ID] [IP]"
		print "  count"
	else:
		main()
