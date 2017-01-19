import sqlite3
from tvMediaApi_dev import TvMedia
import config

conn = sqlite3.connect('uctvDb')
conn.row_factory = sqlite3.Row
c = conn.cursor()


lineupList = ['6305D','41487']
api = TvMedia(config.APIKEY,config.BASE_URL)

for i in lineupList:
    print i

availableLineups = [api.lineup_details(id) for id in lineupList]

c.execute('DELETE FROM uctvLineupsDemo')

conn.commit()



for lineup in availableLineups:
    if lineup:
        for i in lineup['stations']:
            print lineup['lineupID'],i['channelNumber'],i['callsign'],i['name'],i['stationID']

            # sql = '''INSERT INTO uctvLineups (lineupID,channelNumber,channelName,stationID)
            #         VALUES (?,?,?,?)''',(lineup['lineupID'],i['channelNumber'],i['name'],i['stationID'])
            # print sql
            c.execute('''INSERT INTO uctvLineupsDemo(lineupID,channelNumber,callsign,channelName,stationID)
                    VALUES (?,?,?,?,?)''',(lineup['lineupID'],i['channelNumber'],i['callsign'],i['name'],i['stationID']))


conn.commit()






# print lineupDetails.keys()

# print lineupDetails['lineupID']

# for i in lineupDetails['stations']:
#     print i['channelNumber'],i['callsign'],i['name'],i['stationID']
    

#lineupid,channelNumber,callsign,channelName,stationID,logoFileName
# for k, v in lineupDetails.items():



    


