import timehandler as th
import sqlite3
import config

conn = sqlite3.connect('uctvDb')
conn.row_factory = sqlite3.Row
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
		
		# print channelName,HDNo,SDNo,sport,date,startTime,duration,stopTime,event

		db.execute('''INSERT INTO crestronLiveSports (channelName,HDNo,SDNo,sport,date,startTime,duration,stopTime,event)
					values (?,?,?,?,?,?,?,?,?)''',(channelName,HDNo,SDNo,sport,date,startTime,duration,stopTime,event))
	db.commit()

def make_crestron_live_sports_file(db):

	query = db.execute('''SELECT * FROM crestronLiveSports''')
	
	liveSports = [dict(row) for row in query.fetchall()]
	

	with open(config.CRESTRON_LIVE_FILE,'w') as file:
		for i in liveSports:
			# remove sd channel no info for the moment
			del i['SDNo']
			
			event = i['event'].encode('utf8')

			event  = r'<FONT size=""30"" face=""Crestron Sans Pro"" color=""#ffffff"">'+event+'</FONT>'
			line = [i['sport'],event,i['date'],i['startTime'],i['duration'],i['stopTime'],i['channelName'],i['HDNo'],'\n']
			newline = ','.join(str(i) for i in line)
		
			file.write(newline)

def getChannels(db):

	query = db.execute('''SELECT id,channelNumber,callsign,channelName,uctvNo,stationID,lineupID 
						   FROM uctvLineups 
						   WHERE uctvNo != ?
						   ORDER BY uctvNo''',('None',))

	channels = [dict(row) for row in query.fetchall()]

	return channels

def getCrestronLiveSports(db):

	query = db.execute('''SELECT DISTINCT * FROM crestronLiveSports''')
	liveSports = [dict(row) for row in query.fetchall()]
	
	return liveSports

def getLiveSportsWithId(date,start,stop,db):

	query = db.execute('''SELECT * FROM liveSports WHERE date=? and startTime between ? and ?''',(date,start,stop))
	liveSports = [dict(row) for row in query.fetchall()]
	liveSports = th.sort_by_time(liveSports)

	return liveSports

def getLiveSports(date,start,stop,db):

	sdchannels=['NHL Centre Ice 10','NBA League Pass 10']

	query = db.execute('''SELECT DISTINCT channelName,cast(HDNo as text),cast(SDNo as text),date,startTime,duration,sport,event
							 from liveSports 
							 where date = ?
							 and startTime between ? and ?''',(date,start,stop))

	sportslist = [dict(channelName=row[0],HDNo=row[1],SDNo=row[2],date=row[3],startTime=row[4],duration=row[5],sport=row[6],event=row[7]) for row in query.fetchall()]

	for i in sportslist:
		
		
		#add '0' to digital SD channels from sdchannels list
		if  i['channelName'] in sdchannels:
		
			i['SDNo'] = i['SDNo']+'0'
		
		#Remove '0' from analog channels e.g = 23 instead of 23.0
		if i['SDNo']:
			if i['SDNo'][-1] == '0' and i['channelName'] not in sdchannels:
				
				i['SDNo'] = i['SDNo'][0:-2]	

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
		

