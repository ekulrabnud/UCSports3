import sqlite3
import config
from utils import getLiveSports,sort_live_sports,check_for_event
import timehandler as th

conn = sqlite3.connect('uctvdb')
c = conn.cursor()

START = config.DEFAULT_START
STOP = config.DEFAULT_STOP
DATETODAY = th.date_today()

# event = check_for_event(DATETODAY,c)

def crestronLiveSportsUpdate():
	liveSports = getLiveSports(DATETODAY,START,STOP,c)
	sortedLiveSports = sort_live_sports(liveSports,DATETODAY)

	c.execute('''DELETE FROM crestronLiveSports''')
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
		
		print channelName,HDNo,SDNo,sport,date,startTime,duration,stopTime,event

		c.execute('''INSERT INTO crestronLiveSports (channelName,HDNo,SDNo,sport,date,startTime,duration,stopTime,event)
					values (?,?,?,?,?,?,?,?,?)''',(channelName,HDNo,SDNo,sport,date,startTime,duration,stopTime,event))
	conn.commit()





