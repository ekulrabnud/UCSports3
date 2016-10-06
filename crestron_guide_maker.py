import sqlite3
import config

conn = sqlite3.connect('uctvdb')

conn.row_factory = sqlite3.Row
c = conn.cursor()

remove1 = ["NBA League Pass","NHL Centre Ice","NHL League Wide","NHL Centre Ice Extra"]
remove2 = [2.0,
4.0,
4.1,
4.2,
5.0,
6.0,
7.0,
8.0,
9.0,
10.0,
11.0,
12.0,
15.0,
16.0,
17.0,
18.0,
19.0,
20.0,
21.0,
22.0,
24.0,
26.0,
33.0,
34.0,
35.0,
95.0,
95.1,
96.0,
97.0,
99.0]


query = c.execute('''SELECT id,channelNumber,callsign,channelName,uctvNo,stationID,lineupID 
							   FROM uctvLineups 
							   WHERE uctvNo != ?
							   ORDER BY channelName''',('None',))


result = [dict(row) for row in query.fetchall()]


with open(config.CRESTRON_GUIDE_FILE,'w') as file:

	for i in result:
		#strip whitespace
		channelName = i['channelName'].strip()
		#ignore channels in remove 1/2
		if any(channel in channelName for channel in remove1) or i['uctvNo'] in remove2:
			continue
		
		#handle ampersands for html which todate is only an issue with A&E 
		if "&" in channelName:
			channelName = channelName.replace('&','&amp;')
		
		#strings to delete from guide because not needed
		deletes =['HD','Network','Channel','Guide','League','Wide']

		for string in deletes:
			if string  in channelName:
				channelName = channelName.replace(string,'')
			
	
		#build special crestron html
		channel = r'<FONT size=""30"" face=""Crestron Sans Pro"" color=""#ffffff"">'+channelName+'</FONT>'
		uctvNo = str(i['uctvNo'])
		emptyfield = "URL"

		line = channel +','+uctvNo+','+emptyfield+'\n'
		print line
		file.write(line)


		