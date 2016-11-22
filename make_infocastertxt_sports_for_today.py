
import sqlite3
import unicodedata
import sys
import timehandler as th
import config

dir = config.DIR_INFOCASTER_TEXT

#remove accents from words
def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', input_str)
    only_ascii = nkfd_form.encode('ASCII', 'ignore')
    return only_ascii

#Make Infocaster Sports schedule from DB
def make_text_file(date,start,stop):

	print date,start,stop

	try: 
		sdchannels=['NHL Centre Ice 10','NBA League Pass 10']
		
		conn = sqlite3.connect('uctvDb')
		c = conn.cursor()
		f = open(dir+r"\uctvSportsSchedule.txt",'wb')
		
		query = c.execute('''SELECT sport,startTime,event,channelName,HDNo,SDNo 
					from liveSports where date =? and startTime between ? and ?
					order by sport,startTime,event''',(date,start,stop))

		sportslist = [dict(sport=row[0],startTime=row[1],event=row[2],channelName=row[3],HDNo=row[4],SDNo=row[5]) for row in query.fetchall()]	
		
		#convert time from 24 hour to AM/PM
		for i in sportslist:
			i['startTime'] = th.convert_to_am_pm(i['startTime'])
		#Remove accents
		for i in sportslist:
			i['event'] = remove_accents(i['event'])
		for i in sportslist:
			#convert floats to string
			i['SDNo'] = str(i['SDNo'])
			#add '0' to digital SD channels from sdchannels list
			if  i['channelName'] in sdchannels:
				i['SDNo'] = i['SDNo']+'0'
			#Remove '0' from analog channels e.g = 23 instead of 23.0
			if i['SDNo']:
				if i['SDNo'][-1] == '0' and i['channelName'] not in sdchannels:
					
					i['SDNo'] = i['SDNo'][0:-2]
			#Have to limit length of string to 43 characters for the infocaster
			if len(i['event']) > 44:
				i['event'] = i['event'][:45]
			#Build TXT file. Have to add spaces to format and make up for lack of customization in Imagine software

		csport = None
		f.write("\n")
		for i in sportslist:
			sport = i['sport']
			if csport == sport:
				row = ",%s,%s,%s,%s,%s\n" % (i['startTime'],i['event'],i['channelName'],i['HDNo'],i['SDNo'])
				f.write(row)
			else:
				row = "%s,,,,,\n" % i['sport']
				f.write(row)
				row = ",%s,%s,%s,%s,%s\n" % (i['startTime'],i['event'],i['channelName'],i['HDNo'],i['SDNo'])
				f.write(row)
				csport = i['sport']
		print "%s - Text file created at %s" % (th.now(),dir)
	
		conn.close()
		f.close()
	except Exception as e:
		print "Make infocaster Text failed with error %s" % e


# def make_crestron_text_file():

# 	print "make crestron text file function"

# 	date = th.date_today()
# 	event = 'BULLS'
# 	sport = 'basketball'	
# 	start = "01:00:00"
# 	stop ="23:00:00"

# 	try:
		
# 		sdchannels=['NHL Centre Ice 10','NBA League Pass 10']
		
# 		conn = sqlite3.connect('uctvDb')
# 		c = conn.cursor()
# 		f = open(dir+r"\crestronSportsSchedule.txt",'wb')
		
# 		query = c.execute('''SELECT sport,time,event,chName,uctvHDNo,uctvSDNo 
# 					from sportsShed where thedate =? and time between ? and ?
# 					order by sport,time,event''',(date,start,stop))

# 		sportslist = [dict(sport=row[0],time=row[1],event=row[2],chName=row[3],HD=row[4],SD=row[5]) for row in query.fetchall()]	
		
# 		#convert time from 24 hour to AM/PM
# 		for i in sportslist:
# 			i['time'] = th.convert_to_am_pm(i['time'])
# 		#Remove accents
# 		for i in sportslist:
# 			i['event'] = remove_accents(i['event'])
# 		for i in sportslist:
# 			#convert floats to string
# 			i['SD'] = str(i['SD'])
# 			#add '0' to digital SD channels from sdchannels list
# 			if  i['chName'] in sdchannels:
# 				i['SD'] = i['SD']+'0'
# 			#Remove '0' from analog channels e.g = 23 instead of 23.0
# 			if i['SD']:
# 				if i['SD'][-1] == '0' and i['chName'] not in sdchannels:
					
# 					i['SD'] = i['SD'][0:-2]
# 			#Have to limit length of string to 43 characters for the infocaster
# 			if len(i['event']) > 44:
# 				i['event'] = i['event'][:45]
# 			#Build TXT file. Have to add spaces to format and make up for lack of customization in Imagine software

# 		# csport = None
# 		# f.write("\n")
# 		# for i in sportslist:
# 		# 	sport = i['sport']
# 		# 	if csport == sport:
# 		# 		row = ",%s,%s,%s,%s,%s\n" % (i['time'],i['event'],i['chName'],i['HD'],i['SD'])
# 		# 		f.write(row)
# 		# 	else:
# 		# 		row = "%s,,,,,\n" % i['sport']
# 		# 		f.write(row)
# 		# 		row = ",%s,%s,%s,%s,%s\n" % (i['time'],i['event'],i['chName'],i['HD'],i['SD'])
# 		# 		f.write(row)
# 		# 		csport = i['sport']

# 		if event == 'BULLS':
# 			print 'BULLS'
# 			sport = "Basketball"
# 			first = [i for i in sportslist if "Atlanta Hawks" in i['event']]
# 			print first,
# 			second = [i for i in sportslist if i['sport'] == sport and "Atlanta Hawks" not in i['event']]
# 			print second
# 			third = [i for i in sportslist if i['sport'] == "Hockey"]
# 			print third

				


# 				# if i['sport'] == 'Basketball':
# 				# 	row = ",%s,%s,%s,%s,%s\n" % (i['time'],i['event'],i['chName'],i['HD'],i['SD'])
# 				# 	f.write(row)










# 		elif event == 'HAWKS':
# 			print "HAWKS"
# 			sport = "hockey"
# 		else:
# 			print "NO SPORT"



# 		# print "%s - Text file created at %s" % (th.now(),dir)
	
# 		conn.close()
# 		f.close()
# 		print "made crestron file"
# 	except Exception as e:
# 		print "Make infocaster Text failed with error %s" % e
	

	
##########################################################################################

def dbtest():

	conn = sqlite3.connect('uctvDb')
	c = conn.cursor()
	query = c.execute('''SELECT * from channels;''')
	for i in query.fetchall():
		print i



##########################################################################################




	







