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

START = '2016-11-09 00:00:00'
STOP = '2016-11-09 11:59:59'

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

def get_lineup_listings(start,stop,lineups):

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
						
						cursor.execute('''INSERT INTO liveSports (stationID,date,startTime,duration,stopTime,sport,event)
										VALUES (?,?,?,?,?,?,?)''',(stationID,date,startTime,duration,stopTime,sport,event))
	except Exception as e:
		print "Get Lineups Listings failed with error %s" % e

						
	cursor.execute('''UPDATE liveSports
					SET 
					uctvNo = (SELECT uctvNo FROM uctvLineups WHERE uctvLineups.stationID = liveSports.stationID),
					channelName = (SELECT channelName FROM uctvLineups WHERE uctvLineups.stationID = liveSports.stationID)	''')
	conn.commit()

	cursor.execute('''DELETE FROM liveSports
					WHERE id
					IN (SELECT id FROM liveSports
					GROUP BY stationID,channelName,date,startTime
					HAVING COUNT(*) >1) ''')
	conn.commit()
										
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
	
def get_Sports():

	query = cursor.execute('''SELECT uctvLineups.channelName,uctvLineups.uctvNo,liveSports.event,liveSports.date,liveSports.startTime
							FROM uctvLineups
							INNER JOIN liveSports
							ON uctvLineups.stationID = liveSports.stationID
							WHERE uctvLineups.crestron = 0''')

	for i in query.fetchall():
		print i
						
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

	print start,stop

	query = cursor.execute('''SELECT event,startTime,sport,liveSports.uctvNo,liveSports.channelName,uctvLineups.hd
							FROM liveSports
							INNER JOIN uctvLineups
							ON liveSports.stationID = uctvLineups.stationID
							WHERE date = ? AND startTime between ? AND ?  
							ORDER BY sport,startTime,event''',(date,start,stop))
	listings = [dict(row) for row in query.fetchall()]

	csport = None

	with open('testinfocaster.txt','w') as f:

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



get_lineup_listings(START,STOP,LINEUPS)

make_infocaster_file()

# 
