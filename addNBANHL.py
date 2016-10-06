#Added NBA and NHl packages to our lineup using this module

from tvGuide import TVAPI 

import sqlite3

TV = TVAPI()


conn = sqlite3.connect('uctvDb')
c = conn.cursor()

TV.get_lineupsByID()
chicago = TV.chicago_lineup_channels
chicago_OTA = TV.chicago_lineup_channels_OTA
montreal = TV.montreal_lineup_channels

all_lineups = [chicago,chicago_OTA,montreal]

query = c.execute('''SELECT * FROM uctvlineups''')
uctvlineups = query.fetchall()
stationIDs = [i[5] for i in uctvlineups]


for lineup in all_lineups:
	lineupID = lineup['lineupID']
	for i in lineup['stations']:
		if i['stationID'] not in stationIDs and 'MLB' not in i['name']:
			c.execute('''insert into uctvlineups (lineupID,channelNumber,callsign,name,stationID,logoFilename,uctvNo)
 			 values (?,?,?,?,?,?,?)''', (lineupID,i['channelNumber'],i['callsign'],i['name'],i['stationID'],i['logoFilename'],None))
conn.commit()
			

