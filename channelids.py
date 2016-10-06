import tvguide
import config
import sqlite3


TV = tvguide.TVAPI(config.APIKEY)


conn = sqlite3.connect('uctvDb')
c = conn.cursor()
c.execute('''DROP TABLE channelids''')
c.execute('''DROP TABLE if exists comcastchannelids''')
c.execute('''CREATE TABLE comcastchannelids(name text,id integer) ''')

# testlist = [['a',1],['b',2]]



# for i in testlist:
# 	print i[0],i[1]

# 	c.execute('''INSERT INTO channelids(name,id)
# 				VALUES(?,?)''',(i[0],i[1]))
# conn.commit()

TV.get_lineupsByID()

comcast = TV.chicago_lineup_channels

# for key,value in comcast.items():
# 	# print type(comcast['stations'])
# 	for i in comcast['sta']

for i in comcast['stations']:
	c.execute('''INSERT INTO comcastchannelids(name,id)
				VALUES(?,?)''',(i['name'], i['stationID']))
	# print i['name'], i['stationID']
conn.commit()

# # c.execute(''' INSERT INTO sports (stationID,thedate,time,sport,event)
# # 							VALUES (?,?,?,?,?)''',(stationID,thedate,time,sport,event))