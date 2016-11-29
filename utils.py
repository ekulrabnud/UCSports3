import timehandler as th
import sqlite3
import config
import codecs
import sys
from tvMediaApi_dev import TvMedia

api = TvMedia(config.APIKEY,config.BASE_URL)

reload(sys)
sys.setdefaultencoding('utf-8')


# conn = sqlite3.connect('uctvDb')
# conn.row_factory = sqlite3.Row
# # conn.text_factory = str
# cursor = conn.cursor()
 
START = config.DEFAULT_START
STOP = config.DEFAULT_STOP
DATETODAY = th.date_today()

def get_lineup_listings(start,stop,date,lineups,cursor):

	print "Getting Lineup Listings"

	times = th.get_date_times()
	
	query = cursor.execute('''SELECT stationID from uctvLineups WHERE uctvNo != ?''',('OFF',))
	stationIDs = [i[0] for i in query.fetchall()]
	
	cursor.execute('''DELETE FROM liveSports''')
	cursor.execute('''DELETE FROM crestronLiveSports''')
	
	cursor.connection.commit()

	try:
		for time in times:
			listings = [api.lineup_listings(i,start=time[0],stop=time[1],sportEventsOnly=1,liveOnly=1) for i in lineups]
			
			for lineup in listings:
				
				for i in lineup:
					if i['stationID'] in stationIDs :

						if i['live'] and i['team1']:
							event = i['team1'] + ' at '+ i['team2']
						
						elif i['live'] and i['event']:
							event = i['event']
						
						elif i['live'] and i['showName'] == "UFC Fight Night":
							event = i['location'] 

						startTime = th.format_time(th.convert_utc_to_local(i['listDateTime']))
						date = startTime[0]
						startTime = startTime[1]
						duration = i['duration']
						sport = i['showName']
						stationID = i['stationID']
						stopTime = th.addTime(startTime,duration)
						
						cursor.execute('''INSERT INTO liveSports (stationID,date,startTime,duration,stopTime,sport,event)
										VALUES (?,?,?,?,?,?,?)''',(stationID,date,startTime,duration,stopTime,sport,event))
	except Exception as e:
		print "Get Lineups Listings failed with error %s" % e

						
	cursor.execute('''UPDATE liveSports
					SET 
					uctvNo = (SELECT uctvNo FROM uctvLineups WHERE uctvLineups.stationID = liveSports.stationID),
					channelName = (SELECT channelName FROM uctvLineups WHERE uctvLineups.stationID = liveSports.stationID)	''')
	cursor.connection.commit()

	cursor.execute('''DELETE FROM liveSports
					WHERE id
					IN (SELECT id FROM liveSports
					GROUP BY stationID,channelName,date,startTime
					HAVING COUNT(*) >1) ''')
	cursor.connection.commit()
										
	cursor.execute('''INSERT INTO crestronLiveSports (channelName,uctvNo,sport,date,startTime,duration,stopTime,event)
			SELECT 	uctvLineups.channelName,
					uctvLineups.uctvNo,
					liveSports.sport,
					liveSports.date,
					liveSports.startTime,
					liveSports.stopTime,
					liveSports.duration,
					liveSports.event
			FROM livesports
			INNER JOIN uctvLineups
			ON uctvLineups.stationID = liveSports.stationID
			WHERE uctvlineups.crestron = 1 ''')
								
	cursor.connection.commit()

def make_infocaster_file(startTime,stopTime,date,cursor):

	start = startTime
	stop = stopTime

	print start,stop

	query = cursor.execute('''SELECT event,startTime,sport,liveSports.uctvNo,liveSports.channelName,uctvLineups.hd
							FROM liveSports
							INNER JOIN uctvLineups
							ON liveSports.stationID = uctvLineups.stationID
							WHERE date = ? AND startTime between ? AND ?  
							ORDER BY sport,startTime,event''',(date,start,stop))

	listings = [dict(row) for row in query.fetchall()]

	csport = None

	with open(config.INFOCASTER_TEXT_FILE,'w') as f:

		for i in listings:

			startTime = th.convert_to_am_pm(i['startTime'])
			
			hd = i['uctvNo'] if i['HD'] else ''
			sd = i['uctvNo'] if not i['HD'] else ''

			event = i['event'] if not len(i['event']) > 44 else i['event'][:45]
		
			if csport == i['sport']:
				row = ",%s,%s,%s,%s,%s\n" % (startTime,i['event'],i['channelName'],hd,sd)
				f.write(row)

			else:
				row = "%s,,,,,\n" % i['sport']
				f.write(row)
				row = ",%s,%s,%s,%s,%s\n" % (startTime,i['event'],i['channelName'],hd,sd)
				f.write(row)
				csport = i['sport']

def make_crestron_live_sports_file(date,cursor):

	query = cursor.execute('''SELECT * FROM crestronLiveSports WHERE date = ?''',(date,))
	
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
							AND  startTime BETWEEN ? AND ? AND uctvLineups.uctvNo != ? OR ? ''',(date,start,stop,'OFF'))

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

# make_crestron_live_sports_file(cursor)
		

