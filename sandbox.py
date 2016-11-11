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

	
	cursor.execute('''DELETE FROM liveSports''')
	cursor.execute('''CREATE TEMP TABLE listings (stationID Integer,date text,startTime Text,duration Integer,sport Text,event Text) ''')

	conn.commit()

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
					
					cursor.execute('''INSERT INTO listings (stationID,date,startTime,duration,sport,event)
									 VALUES (?,?,?,?,?,?)''',(stationID,date,startTime,duration,sport,event))
					cursor.execute('''INSERT INTO liveSports (channelName,stationID,uctvNo,date,startTime,duration,sport,event)
									SELECT DISTINCT channelName,listings.stationID,uctvNo,date,startTime,duration,sport,event
									FROM uctvLineups
									INNER JOIN listings
									ON uctvLineups.stationID = listings.stationID ''' )

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
# def test():
# 	c.execute('''DELETE FROM liveSports''')


# for lineup in listings:
# 			for i in lineup:
# 				if i['stationID'] in stationIDs :
			
# 					if i['live'] and i['team1']:
# 						datetime = th.format_time(th.convert_utc_to_local(i['listDateTime']))
# 						thedate = datetime[0]
# 						time = datetime[1]
# 						duration = i['duration']
# 						sport = i['showName'].encode('utf8')
# 						event = i['team1'] + ' at '+ i['team2']
# 						stationID = i['stationID']
# 						print stationID,event,sport,duration,time,thedate


# 						cursor.execute(''' INSERT INTO sports (stationID,thedate,time,duration,sport,event)
# 							VALUES (?,?,?,?,?,?)''',(stationID,thedate,time,duration,sport,event))


# 					elif i['live'] and i['event'] :
# 						startTime = th.format_time(th.convert_utc_to_local(i['listDateTime']))
# 						thedate = startTime[0]
# 						time = startTime[1]
# 						duration = i['duration']
# 						sport = i['showName'].encode('utf8')
# 						event = i['event'].encode('utf-8')
# 						stationID = i['stationID']
# 						print stationID,event,sport,duration,time,thedate
						
				
# 						cursor.execute(''' INSERT INTO sports (stationID,thedate,time,duration,sport,event)
# 							VALUES (?,?,?,?,?,?)''',(stationID,thedate,time,duration,sport,event))

# 					#had to put this as last minute fix in since UFC is not considered and event and therefore conditional failed.
# 					elif i['live'] and i['showName'] == "UFC Fight Night":
					
# 						startTime = th.format_time(th.convert_utc_to_local(i['listDateTime']))
# 						thedate = startTime[0]
# 						time = startTime[1]
# 						duration = i['duration']
# 						sport = i['showName'].encode('utf8')
# 						#note event is actually location.
# 						event = i['location']
# 						stationID = i['stationID']

# 						cursor.execute(''' INSERT INTO sports (stationID,thedate,time,duration,sport,event)
# 							VALUES (?,?,?,?,?,?)''',(stationID,thedate,time,duration,sport,event))

# 					# First delete old data from sports schedule
# 		cursor.execute('''DELETE FROM liveSports''')

# 		cursor.execute('''INSERT INTO liveSports (channelName,))

# 			# get the last date from sports schedule
# 			# c.execute('''SELECT max(thedate) from liveSports;''')
# 			# maxDate = c.fetchone()
# 			# Insert any new data into sports schedule
# 		# cursor.execute('''INSERT INTO liveSports (channelName,stationId,HDNo,SDNo,date,startTime,duration,sport,event)
# 		# 				 SELECT DISTINCT channelName,sports.stationID,HDNo,SDNo,thedate,time,duration,sport,event 
# 		# 				 from uctvLineupsSport
# 		# 				 INNER JOIN sports
# 		# 				 ON uctvLineupsSport.hdStationID = sports.stationID;''')

		
# 	conn.commit()
# 	conn.close()
		






