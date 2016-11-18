import timehandler as th
import sqlite3
import config
import codecs
import sys

reload(sys)
sys.setdefaultencoding('utf-8')


conn = sqlite3.connect('uctvDb')
conn.row_factory = sqlite3.Row
# conn.text_factory = str
cursor = conn.cursor()
 
START = config.DEFAULT_START
STOP = config.DEFAULT_STOP
DATETODAY = th.date_today()


def update_crestron_live_sports_db(db):
	
	event = check_for_event(DATETODAY,db)
	liveSports = getLiveSports(DATETODAY,START,STOP,db)
	sortedLiveSports = sort_live_sports(liveSports,DATETODAY,event[0])

	db.execute('''DELETE FROM crestronLiveSports''')

	for i in sortedLiveSports:
		channelName = i['channelName']
		HDNo = i['HDNo']
		SDNo = i['SDNo']
		sport = i['sport']
		date = i['date']
		startTime = th.convert_to_24hr(i['startTime'])
		duration = i['duration']
		stopTime = th.addTime(startTime,duration)
		event = i['event']
		
		

		db.execute('''INSERT INTO crestronLiveSports (channelName,uctvNo,sport,date,startTime,duration,stopTime,event)
					values (?,?,?,?,?,?,?,?,?)''',(channelName,HDNo,SDNo,sport,date,startTime,duration,stopTime,event))
	db.commit()

def make_crestron_live_sports_file(db,date):

	query = db.execute('''SELECT * FROM crestronLiveSports WHERE date = ?''',(date,))
	
	liveSports = [dict(row) for row in query.fetchall()]
	

	with open(config.CRESTRON_LIVE_FILE,'w') as file:
		for i in liveSports:
			
			event = i['event']
			event  = '<FONT size=""30"" face=""Crestron Sans Pro"" color=""#ffffff"">'+event+'</FONT>'
			line = [i['sport'],event,i['date'],i['startTime'],i['duration'],i['stopTime'],i['channelName'],i['uctvNo'],'\n']
			newline = ','.join(i for i in line)
		
			file.write(newline)

def getChannels(db):

	query = db.execute('''SELECT id,channelNumber,callsign,channelName,uctvNo,stationID,lineupID
						   FROM uctvLineups 
						   WHERE uctvNo != ?
						   ORDER BY uctvNo''',('None',))

	channels = [dict(row) for row in query.fetchall()]

	return channels

def getCrestronLiveSports(db):

	print "getting crestron live sport {}".format(th.date_today())

	query = db.execute('''SELECT * FROM crestronLiveSports WHERE date = ?''',(th.date_today(),))
	liveSports = [dict(row) for row in query.fetchall()]
	
	return liveSports

def getLiveSportsWithId(date,start,stop,db):

	query = db.execute('''SELECT * FROM liveSports WHERE date=? and startTime between ? and ?''',(date,start,stop))
	liveSports = [dict(row) for row in query.fetchall()]
	liveSports = th.sort_by_time(liveSports)

	return liveSports

def getLiveSports(date,start,stop,db):

	# sdchannels=['NHL Centre Ice 10','NBA League Pass 10']

	query = db.execute('''  SELECT DISTINCT uctvLineups.channelName,uctvLineups.uctvNo,date,startTime,duration,sport,event,HD
							FROM liveSports 
							INNER JOIN uctvLineups
							ON livesports.stationID = uctvLineups.stationID
							WHERE date = ?
							AND  startTime BETWEEN ? AND ? AND uctvLineups.uctvNo != ? ''',(date,start,stop,'OFF'))

	sportslist = [dict(channelName=row[0],uctvNo=row[1],date=row[2],startTime=row[3],duration=row[4],sport=row[5],event=row[6],HD=row[7]) for row in query.fetchall()]

	# for i in sportslist:
		
		
	# 	#add '0' to digital SD channels from sdchannels list
	# 	if  i['channelName'] in sdchannels:
		
	# 		i['SDNo'] = i['SDNo']+'0'
		
	# 	#Remove '0' from analog channels e.g = 23 instead of 23.0
	# 	if i['SDNo']:
	# 		if i['SDNo'][-1] == '0' and i['channelName'] not in sdchannels:
				
	# 			i['SDNo'] = i['SDNo'][0:-2]	

	sportslist = th.sort_by_time(sportslist)

	return sportslist

def check_for_event(date,db):
	
	query = db.execute('''SELECT * FROM ucEventCalendar WHERE date = ?''',(date,))
	result = query.fetchone()

	if result:
		event_start = result[2]
		event = result[3]
		return event,event_start
	else:
		
		return ("No Event","00:00")

def sort_live_sports(sportslist,date,event=None):

	if event:
			
			if 'Chicago Bulls' in event[0]:
				team = 'Chicago Bulls'
			elif 'Chicago Blackhawks' in event[0]:
				team = 'Chicago Blackhawks'
			else:
				team = 'Chicago'
	else:
		
		team = 'Chicago'

	# checks to make sure team exists in event if not then defaults to other_sport for all Crestron data
	if team:

	
		if any (team in i['event'] for i in sportslist):
			
			uc_team = [i for i in sportslist if team in i['event']]
			# print uc_team
			sport = uc_team[0]['sport']
			# print sport

			uc_sport = [i for i in sportslist if i['sport'] == sport and team not in i['event']]
			# print uc_sport

			uc_other_sport = [i for i in sportslist if i['sport'] != sport and team not in i['event']]
			# print uc_other_sport

			uc_team = sorted(uc_team,key=lambda x:x['startTime'])
			uc_sport = sorted(uc_sport,key= lambda x:x['startTime'])
			other_sport = sorted(uc_other_sport,key=lambda x:x['sport'])

			crestronSorted = uc_team + uc_sport + other_sport
		
			return crestronSorted
		else:
		
			return sportslist


	else:
	
		return sportslist

def updateUctvLineups(columnName,rowid,value):

	cursor.execute('''UPDATE uctvLineups SET {}=? WHERE id=?'''.format(columnName),(value,rowid,))
	conn.commit()

# make_crestron_live_sports_file(cursor)
		

