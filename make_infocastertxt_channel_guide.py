#This does most of the leg work making csv file for channel guide. Manual editing is still needed to reorder some of the NHL and NBA pacakges 
#numerically. Will automate this one day.

import csv
import sqlite3
import sys
import config

dir = config.DIR

conn = sqlite3.connect('uctvDb')
c = conn.cursor()

sdchannels=['NHL Centre Ice 10','NBA League Pass 10']

csvfile = open(dir+"\channelguide.csv",'wb')
channels = csv.writer(csvfile, dialect='excel')

query = c.execute('''SELECT name,uctvNo from uctvlineups where uctvNo != "None" order by name ''')

encoded = [[s.encode('utf-8') if isinstance(s,unicode) else str(s) for s in t ] for t in query.fetchall()]


for i in encoded:
	if  i[0] in sdchannels:
		i[1] = i[1]+'0'
	if i[1][-1] == '0' and i[0] not in sdchannels:
		i[1] = i[1][0:-2]

	row = "%s - %s" % (i[0],i[1])
	print row
	channels.writerow([row])
