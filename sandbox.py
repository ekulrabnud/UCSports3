import utils
import timehandler as th
import sqlite3
import config
from tvMediaApi_dev import TvMedia

api = TvMedia(config.APIKEY,config.BASE_URL)

conn = sqlite3.connect('uctvDb')
conn.text_factory = str
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

START = config.DEFAULT_START
STOP = config.DEFAULT_STOP
DATETODAY = th.date_today()

DATETODAY = th.date_today()
LINEUPS = ['41614D','41487']

def getCrestronSports(liveSports):

	lineups= cursor.execute('''SELECT * from uctvLineups WHERE callSign = ? ''',('GMHD2',))

	for i in lineups.fetchall():
		print i

	#Select all 
	query = c.execute('''SELECT * FROM liveSports 
							  WHERE stationId IN (SELECT stationId FROM uctvLineups WHERE crestron = 1 AND uctvNo != ?)
						      AND date = ? ''',('',DATETODAY))

	crestronLiveSports = [i for i in query.fetchall()]
	for i in crestronLiveSports:
		print i

	return crestronLiveSports

def get_stationIDs():

	query = cursor.execute('''SELECT stationID from uctvLineups WHERE uctvNo != ?''',('OFF',))
	stationIDs = [i[0] for i in query.fetchall()]

	return stationIDs

def combiner(listings):

	seen = []
	newRows = []
	
	for i in listings:
		
		if i['listingID'] not in seen:
			i['SD'] = i['uctvNo'] if i['HD'] == None else ''
			seen.append(i['listingID']);	
		else:
			row = [x for x in listings if x['listingID']==i['listingID']]
			print row[0]['HD'],row[0]['uctvNo'],row[1]['HD'],row[1]['uctvNo']
			uctvNo = row[0]['uctvNo'] if row[0]['HD'] == 1 else row[1]['uctvNo']		
			SD = row[1]['uctvNo'] if row[1]['HD'] == None else row[0]['uctvNo']
			HD = row[0]['HD']
			listingID = row[0]['listingID']
			event = row[0]['event']
			sport = row[0]['sport']
			channelName = row[0]['channelName']
			startTime = row[0]['startTime']
			newRow = {'sport':sport,'event':event,'listingID':listingID,'HD':HD,'SD':SD,'channelName':channelName,'uctvNo':uctvNo,'startTime':startTime}
			newRows.append(newRow)

	newRowIds = [x['listingID'] for x in newRows]
	newlistings = [x for x in listings if x['listingID'] not in newRowIds]

	return newRows + newlistings	

def get_live_sports():

		query = cursor.execute('''  SELECT uctvLineups.uctvNo,liveSports.channelName,listingID,HD,sport,event,startTime
							FROM liveSports 
							INNER JOIN uctvLineups
							ON livesports.stationID = uctvLineups.stationID
							WHERE date = ? 
							AND  startTime BETWEEN ? AND ? AND uctvLineups.uctvNo != ? OR ? ''',(DATETODAY,START,STOP,'OFF','None'))

		liveSports = [dict(row) for row in query.fetchall()]
		
		# for i in liveSports:
		# 	print i
		
		newListings = combiner(liveSports)

		# for i in newListings:
		# 	print i['uctvNo'],i['SD'],i['listingID'],i['event']		
						
def update_crestron_live_sports_db():

	cursor.execute('''DELETE FROM crestronLiveSports''')

	query = cursor.execute('''INSERT INTO crestronLiveSports (channelName,uctvNo,event,sport, date,startTime,duration)
							SELECT uctvLineups.channelName,uctvLineups.uctvNo,liveSports.event,liveSports.sport,liveSports.date,liveSports.startTime,liveSports.duration
							FROM uctvlineups
							INNER JOIN liveSports
							ON uctvLineups.stationID = liveSports.stationID
							WHERE uctvlineups.crestron = 1 ''')
	conn.commit()
	conn.close()

def make_lineups(lineups):

	c.execute('''DELETE FROM uctvLineups''')

	for lineup in lineups:
		resp = api.lineup_details(lineup)
		for i in resp['stations']:
			lineupID = lineup
			channelName = i['name']
			print channelName
			channelNumber = i['channelNumber']
			callsign = i['callsign']
			channelNumber = i['channelNumber']
			stationID = i['stationID']
			logoFilename = i['logoFilename']


			c.execute('''INSERT INTO uctvLineups (lineupID,channelNumber,channelName,callsign,stationID,logoFilename)
				VALUES (?,?,?,?,?,?)''',(lineupID,channelNumber,channelName,callsign,stationID,logoFilename))
	conn.commit()

def make_infocaster_file(startTime,stopTime,date):

	start = startTime
	stop = stopTime

	query = cursor.execute('''  SELECT uctvLineups.uctvNo,liveSports.channelName,listingID,HD,sport,event,startTime
							FROM liveSports 
							INNER JOIN uctvLineups
							ON livesports.stationID = uctvLineups.stationID
							WHERE date = ? 
							AND  startTime BETWEEN ? AND ? AND uctvLineups.uctvNo != ? OR ?
							ORDER BY sport,startTime ''',(date,start,stop,'OFF','None'))

	listings = [dict(row) for row in query.fetchall()]

	newListings = combiner(listings)



	# newlistings = th.sort_by_time(newListings)
	sortedListings = sorted(newListings, key=lambda k: (k['sport'],k['startTime'])) 
	# sortedListings = sorted(sortedListings, key=lambda k: k['startTime']) 
	csport = None
	
	with open('testinfocaster.txt','w') as f:

		for i in sortedListings:

			# startTime = th.convert_to_am_pm(i['startTime'])
			
			# hd = i['uctvNo'] if i['HD'] else ''
			# sd = i['uctvNo'] if not i['HD'] else ''

			event = i['event'] if not len(i['event']) > 44 else i['event'][:45]
		
			if csport == i['sport']:
				row = ",%s,%s,%s,%s,%s\n" % (i['startTime'],i['event'],i['channelName'],i['uctvNo'],i['SD'])
				f.write(row)

			else:
				row = "%s,,,,,\n" % i['sport']
				f.write(row)
				row = ",%s,%s,%s,%s,%s\n" % (i['startTime'],i['event'],i['channelName'],i['uctvNo'],i['SD'])
				f.write(row)
				csport = i['sport']

def get_lineup_listingsver1(lineups):

	print "Getting Lineup Listings"

	times = th.get_date_times()


	
	query = cursor.execute('''SELECT stationID from uctvLineups WHERE uctvNo != ?''',('OFF',))
	stationIDs = [i[0] for i in query.fetchall()]
	
	cursor.execute('''DELETE FROM liveSports''')
	cursor.execute('''DELETE FROM crestronLiveSports''')
	
	conn.commit()

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
						listingID = i['listingID']
						
						cursor.execute('''INSERT INTO liveSports (stationID,date,startTime,duration,stopTime,sport,event,listingID)
										VALUES (?,?,?,?,?,?,?,?)''',(stationID,date,startTime,duration,stopTime,sport,event,listingID))
	except Exception as e:
		print "Get Lineups Listings failed with error %s" % e

						
	cursor.execute('''UPDATE liveSports
					SET 
					uctvNo = (SELECT uctvNo FROM uctvLineups WHERE uctvLineups.stationID = liveSports.stationID),
					channelName = (SELECT channelName FROM uctvLineups WHERE uctvLineups.stationID = liveSports.stationID)	''')


	cursor.execute('''DELETE FROM liveSports
					WHERE listingID
					IN (SELECT listingID FROM liveSports
					GROUP BY stationID,channelName,date,startTime
					HAVING COUNT(*) >1) ''')
	
										
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
								
	conn.commit()

def get_lineup_listingsver2(lineups):

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
										
	cursor.execute('''INSERT INTO crestronLiveSports (channelName,uctvNo,sport,date,startTime,stopTime,duration,event)
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

def listingsTest(lineups):

	START = '2016-11-29 00:00:00'
	STOP = '2016-11-29 11:59:59'

	listings = [api.lineup_listings(i,start=START,stop=STOP,sportEventsOnly=1,liveOnly=1) for i in lineups]


	for lineup in listings:
		for i in lineup:
			print i['stationID'],i['name'],i['team1'],i['listingID']

def make_crestron_live_sports_file(date):

	query = cursor.execute('''SELECT * FROM crestronLiveSports WHERE date = ?''',(date,))
	
	liveSports = [dict(row) for row in query.fetchall()]
	
	with open(config.CRESTRON_LIVE_FILE,'w') as file:

		for i in liveSports:
			event = i['event']
			event  = '<FONT size=""30"" face=""Crestron Sans Pro"" color=""#ffffff"">'+event+'</FONT>'
			line = [i['sport'],event,i['date'],i['startTime'],str(i['duration']),i['stopTime'],i['channelName'],i['uctvNo'],'\n']
			print line
			newline = ','.join(i for i in line)
		
			file.write(newline)
			
#get_lineup_listingsver2(LINEUPS)
#make_crestron_live_sports_file(DATETODAY)
#get_Sports()
# listingsTest(LINEUPS)
make_infocaster_file(START,STOP,DATETODAY)


