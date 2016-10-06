import feedparser
from datetime import datetime ,timedelta
import sqlite3



conn = sqlite3.connect('uctvDb')
c = conn.cursor()
#deletes all events from table each time function runs


def get_events():

	''' Connects to rss feed of UC calendar. Parses event and dates and inserts into db. Note rss feed for events which 
	span multiple days simply gives beginning and end date. If this is the case conditional inserts missing dates'''
	#create rss parser object using URL below
	rss = feedparser.parse('http://www.unitedcenter.com/rss/events.aspx')
	#connect to db

	#deletes all events from table each time function runs
	c.execute('''DELETE FROM ucEventCalendar''')

	for i in rss['entries']:
		event = i['title']
		date = i['event_date']
		# Conditional inserts new actual dates for events spanning datemin "-" date max

		if "-" in date:
			dates = date.split('-')
			# removes named day "CST" and trailing whitespace
			dates = [ i.split(',')[1].strip()[:-4] for i in dates]
			#convert string dates to datetime objects
			dateMax = datetime.strptime(dates[1],"%d %b %Y %H:%M:%S")
			dateMin = datetime.strptime(dates[0],"%d %b %Y %H:%M:%S")
			#derive duration of event days
			total_event_days = dateMax - dateMin
			#loop through events and add missing dates
			for i in range(0,abs(total_event_days.days)+1):

				date = dateMin + timedelta(days=i)
				dbinsert(date,event)
			
		else:
			# removes named day "CST" and trailing whitespace
			date = date.split(',')[1].strip()[:-4]
	
			#convert string dates to datetime objects
			date = datetime.strptime(date,"%d %b %Y %H:%M:%S")
			dbinsert(date,event)



def dbinsert(date,event):

		_date = date.strftime('%Y-%m-%d')
		_time = date.strftime('%H:%M:%S')

	

		c.execute(''' INSERT INTO ucEventCalendar (date,time,event)
								VALUES (?,?,?)''',(_date,_time,event))
		conn.commit()
		





		
get_events()

			


		
