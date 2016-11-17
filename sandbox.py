import utils
import timehandler as th
import sqlite3
import config
from tvMediaApi_dev import TvMedia

api = TvMedia(config.APIKEY,config.BASE_URL)

conn = sqlite3.connect('uctvDb')
conn.text_factory = str
# conn.row_factory = sqlite3.Row
cursor = conn.cursor()

START = '2016-11-09 00:00:00'
STOP = '2016-11-09 11:59:59'

DATETODAY = th.date_today()
LINEUPS = ['41614D','41487']

# START,STOP = th.sevenDay_start_stop_time()


# LiveSports(DATETODAY,START,STOP,conn)
# liveSports = utils.get

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

	times = th.get_date_times()
	stationIDs = get_stationIDs()
	print stationIDs

	cursor.execute('''DELETE FROM liveSports''')
	cursor.execute('''DELETE FROM crestronLiveSports''')
	
	conn.commit()

	for time in times:
		listings = [api.lineup_listings(i,start=time[0],stop=time[1],sportEventsOnly=1,liveOnly=1) for i in lineups]
		print len(listings)
		for lineup in listings:
			print len(lineup)
			for i in lineup:
				if i['stationID'] in stationIDs :

					print i['live'],i['event'],i['team1']


					
			
					if i['live'] and i['team1']:
						event = i['team1'] + ' at '+ i['team2']
						print 'team1' + i['event'] 
					elif i['live'] and i['event']:
						event = i['event']
						print 'event' + i['event'] 
					elif i['live'] and i['showName'] == "UFC Fight Night":
						event = i['location'] 


					startTime = th.format_time(th.convert_utc_to_local(i['listDateTime']))
					date = startTime[0]
					startTime = startTime[1]
					duration = i['duration']
					sport = i['showName']
					stationID = i['stationID']
					print startTime
					stopTime = th.addTime(startTime,duration)
					

					cursor.execute('''INSERT INTO liveSports (stationID,date,startTime,duration,stopTime,sport,event)
									VALUES (?,?,?,?,?,?,?)''',(stationID,date,startTime,duration,stopTime,sport,event))
					
	#upates the Crestron Live Sports table
	conn.commit()
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
										
	cursor.execute('''INSERT INTO crestronLiveSports (channelName,uctvNo,stationID,event,sport,date,startTime,stopTime,duration)
			SELECT 	uctvLineups.channelName,
					uctvLineups.uctvNo,
					liveSports.stationID,
					liveSports.event,
					liveSports.sport,
					liveSports.date,
					liveSports.startTime,
					liveSports.stopTime,
					liveSports.duration
			FROM uctvlineups
			INNER JOIN liveSports
			ON uctvLineups.stationID = liveSports.stationID
			WHERE uctvlineups.crestron = 1 ''')

									
	conn.commit()
	
	conn.close()

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
# make_lineups(LINEUPS)
# print th.get_date_times()
# print get_stationIDs()
get_lineup_listings(START,STOP,LINEUPS)
# update_crestron_live_sports_db()
# update_crestron_live_sports_db()
