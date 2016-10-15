from tvMediaApi import API
import sqlite3
import timehandler as th
import config

# START = config.DEFAULT_START
# STOP = config.DEFAULT_STOP



api = API(config.APIKEY)

def get_sport_listings(start,stop):

	'''This function gets all the station ids from our channel lineup. This does not include all ids since some of them e.g VH1
		do not show sports. The ids are used to build a request to the API whose response is then parsed and inserted into 
		sportshed table'''

	try:
		conn = sqlite3.connect('uctvDb')
		c = conn.cursor()

		c.execute('''CREATE TEMP TABLE sports (stationID Integer,thedate text,time Text,duration Integer,sport Text,event) ''')
		
		#Get all the sports station ids. Note NHL and NBA packages dropped at end of regular season so these channels are ommitted by
		#ignoring ids < 45 for NHL and < 33 for NHL and NBA

		# comcast = c.execute('''SELECT hdstationID from uctvLineupsSport where lineupId = "41614D" and id not between 33 and 43;''')
		comcast = c.execute('''SELECT hdstationID from uctvLineupsSport where lineupId = "41614D" ;''')
		
		#comcast = c.execute('''SELECT hdstationID from uctvLineupsSport where lineupId = "41614D";''')
		comcast = ','.join([ (str(i[0])) for i in comcast.fetchall()])
		bell = c.execute('''SELECT hdstationID from uctvLineupsSport where lineupID = "41487"; ''')
		# print comcast
		bell = ','.join([ (str(i[0])) for i in bell.fetchall()])
		# print bell
	
		#Format Request
		requestdata = {'41614D':comcast,'41487':bell}


		#Request data from API #######################################################################################################
		response = [i for i in api.get_sport(start,stop,requestdata)]
		
		
		#Parse response and insert into sporsShed table
	
		for lineups in response:
			for channel in lineups:
				stationID = channel['channel']['stationID']
				for i in channel['listings']:
				

					# parses from team versus team sports
					if i['live'] and i['team1']:
						datetime = th.format_time(th.convert_utc_to_local(i['listDateTime']))
						thedate = datetime[0]
						time = datetime[1]
						duration = i['duration']
						sport = i['showName'].encode('utf8')
						event = i['team1'] + ' at '+ i['team2']
						
						c.execute(''' INSERT INTO sports (stationID,thedate,time,duration,sport,event)
							VALUES (?,?,?,?,?,?)''',(stationID,thedate,time,duration,sport,event))

					# parses for no team v team sports
					elif i['live'] and i['event'] :
						startTime = th.format_time(th.convert_utc_to_local(i['listDateTime']))
						thedate = startTime[0]
						time = startTime[1]
						duration = i['duration']
						sport = i['showName'].encode('utf8')
						event = i['event']
				
						c.execute(''' INSERT INTO sports (stationID,thedate,time,duration,sport,event)
							VALUES (?,?,?,?,?,?)''',(stationID,thedate,time,duration,sport,event))

					#had to put this as last minute fix in since UFC is not considered and event and therefore conditional failed.
					elif i['live'] and i['showName'] == "UFC Fight Night":
					
						startTime = th.format_time(th.convert_utc_to_local(i['listDateTime']))
						thedate = startTime[0]
						time = startTime[1]
						duration = i['duration']
						sport = i['showName'].encode('utf8')
						#note event is actually location.
						event = i['location']

						c.execute(''' INSERT INTO sports (stationID,thedate,time,duration,sport,event)
							VALUES (?,?,?,?,?,?)''',(stationID,thedate,time,duration,sport,event))



		# First delete old data from sports schedule
		c.execute('''DELETE FROM liveSports''')

		# get the last date from sports schedule
		# c.execute('''SELECT max(thedate) from liveSports;''')
		# maxDate = c.fetchone()
		# Insert any new data into sports schedule
		c.execute('''INSERT INTO liveSports (channelName,HDNo,SDNo,date,startTime,duration,sport,event)
						 SELECT DISTINCT channelName,HDNo,SDNo,thedate,time,duration,sport,event 
						 from uctvLineupsSport
						 INNER JOIN sports
						 ON uctvLineupsSport.hdStationID = sports.stationID;''')

	
		conn.commit()
		conn.close()
		print "Got Sport from %s t0 %s" %(start,stop)
		return False
	except Exception as inst:

		print inst.args
		return False






# # if __name__=="__main__":

# start,stop = th.sevenDay_start_stop_time()
# get_sport_listings(start,stop)




