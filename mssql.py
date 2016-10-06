# Remote Desktop - arndbutl02
# Start - MS SQL Server 2008 R2
# user = sandbox
# pass = pdb4sbox$

#Copies needed tables from sqlite to Microsoft SQL (SERVER=ARNDBUTL02;PORT=1433;DATABASE=Sandbox;UID=sandbox;PWD=pdb4sbox$)
import pyodbc
import sqlite3


sqlite_cnxn = sqlite3.connect('uctvDb')
msql_cnxn = pyodbc.connect('DRIVER={SQL Server Native Client 11.0};SERVER=ARNDBUTL02;PORT=1433;DATABASE=Sandbox;UID=sandbox;PWD=pdb4sbox$')


sqlite3_cursor = sqlite_cnxn.cursor()
msql_cursor = msql_cnxn.cursor()


#################Sports Schedule####################

sqlite3_cursor.execute(" SELECT * FROM sportsShed ")
sqlite3_sportShed = sqlite3_cursor.fetchall()

msql_cursor.execute("DELETE FROM crestron_Sports")
#resets primary key
msql_cursor.execute("TRUNCATE TABLE crestron_Sports")
# msql_cursor.commit()

for i in sqlite3_sportShed:
	msql_cursor.execute('''INSERT INTO crestron_Sports(chName,uctvHDNo,uctvSDNo,thedate,time,sport,event) 
							VALUES (?,?,?,?,?,?,?)''', i[1],i[2],i[3],i[4],i[5],i[6],i[7])

msql_cursor.commit()

#################Channel Guide####################

sqlite3_cursor.execute('SELECT name,uctvNo from uctvLineups order by uctvNo')
sqlite3_channel_guide = sqlite3_cursor.fetchall()


for i in sqlite3_channel_guide:
	if i[1] != 'None':
		print i
		msql_cursor.execute(''' INSERT INTO crestron_channel_guide(name,uctvNo) VALUES(?,?)''' , i[0],i[1])

msql_cursor.commit()








