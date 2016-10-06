import sqlite3

conn = sqlite3.connect('uctvDb')
c = conn.cursor()

query = c.execute('''SELECT * from liveSports''')


for i in query.fetchall():
	print i