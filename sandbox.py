import utils
import timehandler as th
import sqlite3
import config

conn = sqlite3.connect('uctvDb')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()


START = config.DEFAULT_START
STOP = config.DEFAULT_STOP
DATETODAY = th.date_today()




# print utils.check_for_event(DATETODAY,cursor)
# utils.make_crestron_live_sports_file()
# utils.update_crestron_live_sports_db()
liveSports = utils.getLiveSports(DATETODAY,START,STOP,conn)

def getCrestronSports(liveSports):
	# print liveSports

	query = cursor.execute('''SELECT stationID, channelName
								FROM uctvLineups 
								WHERE crestron = 1 AND uctvNo IS NOT NULL ''')
	for i in query.fetchall():
		print i


	# query = cursor.execute('SELECT * FROM liveSports')

	# for i in query.fetchall():
	# 	print i


getCrestronSports(liveSports)
