import utils
import timehandler as th
import sqlite3
import config
from tvMediaApi_dev import TvMedia

api = TvMedia(config.APIKEY,config.BASE_URL)

conn = sqlite3.connect('uctvDb')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()


DATETODAY = th.date_today()
LINEUPS = ['41614D','41487']

START,STOP = th.sevenDay_start_stop_time()



liveSports = utils.getLiveSports(DATETODAY,START,STOP,conn)

def getCrestronSports(liveSports):

	lineups= cursor.execute('''SELECT * from uctvLineups WHERE callSign = ? ''',('GMHD2',))

	for i in lineups.fetchall():
		print i

	#Select all 
	query = cursor.execute('''SELECT * FROM liveSports 
							  WHERE stationId IN (SELECT stationId FROM uctvLineups WHERE crestron = 1 AND uctvNo != ?)
						      AND date = ? ''',('None',DATETODAY))

	crestronLiveSports = [i for i in query.fetchall()]
	for i in crestronLiveSports:
		print i

	return crestronLiveSports

# getCrestronSports(liveSports)

def get_stationIDs():

	query = cursor.execute('''SELECT stationId from uctvLineups WHERE uctvNo != ?''',('None',))
	stationIDs = [i[0] for i in query.fetchall()]
	return stationIDs

def get_lineup_listings(start,stop,lineups):
	print start,stop,lineups

	# listings = [ api.lineup_listings(i,start=START,stop=STOP,sportEventsOnly=1,liveOnly=1) for i in lineups ]
	stationIDs = get_stationIDs()

	
	listings = [api.lineup_listings(i,start=start,stop=stop,sportEventsOnly=1) for i in lineups ]

	for lineup in listings:
		for i in lineup:
			
			print i['showName'],i['name'],i['listDateTime']
	# print start,stop
	# print len(listings[0]) + len(listings[1])
				


# print get_stationIDs()
# print START,STOP


get_lineup_listings(START,STOP,LINEUPS);





