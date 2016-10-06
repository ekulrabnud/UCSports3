import sqlite3
import unicodedata
import sys



def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = nkfd_form.encode('ASCII', 'ignore')
    return only_ascii

##########################################################################################
#Make Infocaster Channel Guide

# TXTfile = open("channels.TXT",'wb')
# channels = TXT.writer(TXTfile, dialect='excel')

# query = c.execute('''SELECT name,uctvNo from uctvlineups where uctvNo != "None" order by uctvNo ''')

# encoded = [[s.encode('utf-8') if isinstance(s,unicode) else str(s) for s in t ] for t in query.fetchall()]


# for i in encoded:
# 	if  i[0] in sdchannels:
# 		i[1] = i[1]+'0'
# 	row = "%s - %s" % (i[0],i[1])
# 	channels.writerow([row])

##########################################################################################

##########################################################################################
#Make Infocaster Sports schedule from DB
def make_text(date):

		sdchannels=['NHL Centre Ice 10','NBA League Pass 10']
		
		conn = sqlite3.connect('uctvDb')
		c = conn.cursor()
		f = open("S:\Technical Operations\Luke\uctv\uctvSportstxt.txt",'wb')
		query = c.execute('''SELECT sport,time,event,chName,uctvHDNo,uctvSDNo from (SELECT sport,time,event,chName,uctvHDNo,uctvSDNo from sportsShed where thedate =? order by time)
							order by sport''',(date,))
		result = query.fetchall()
		result = [list(i) for i in result]

		#Remove accents
		for i in result:
			i[2] = remove_accents(i[2])

		#encoded = [[s.encode('utf-8') if isinstance(s,unicode) else str(s) for s in t ] for t in result]
		csport = None
		f.write("\n")
		#Fix SD channels that need a 0 and also shorten events longer than 45 characters
		for i in result:
			if  i[4] in sdchannels:
				i[5] = i[5]+'0'
		#Have to limit length of string to 45 characters for the infocaster
			if len(i[2]) > 44:
				i[2] = i[2][:45]
		#Build TXT file have to add spaces to format and make up for lack of customization in Imagine software
		for i in result:
			#space = ""
			sport = i[0]
			if csport == sport:
				row = ",%s,%s,%s,%s,%s\n" % (i[1],i[2],i[3],i[4],i[5])
				f.write(row)
			else:
				row = "%s,,,,,\n" % i[0]
				f.write(row)
				row = ",%s,%s,%s,%s,%s\n" % (i[1],i[2],i[3],i[4],i[5])
				f.write(row)
				print row
				csport = i[0]
		print "TXT Success"
	
		print "Error making TXT"


		conn.close()
##########################################################################################
make_text("2015-02-21")



	







