import sqlite3

conn = sqlite3.connect('uctvDb')
c = conn.cursor()

query = c.execute('''SELECT event from crestronLiveSports''')


events = [i[0].encode('ascii','ignore') for i in query.fetchall()]

print events

with open('tester.txt','w') as f:
	for i in events:
		line = [i[0],i[0],i[0]]
		newline = ','.join(str(i) for i in line)
		f.write(newline)
		

