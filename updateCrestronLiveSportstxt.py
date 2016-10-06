
import sqlite3
import timehandler as th
import config
from parse_uc_calendar import get_events,dbinsert


conn = sqlite3.connect('uctvDb')
conn.row_factory = sqlite3.Row
c = conn.cursor()

START = config.DEFAULT_START
STOP = config.DEFAULT_STOP
TEST_EVENT_DATE = "2016-Aug-28" 
CRESTRON_LIVE_FILE = config.CRESTRON_LIVE_FILE 


date_today = th.date_today()
event_date=th.date_today_withMonth()




if __name__=="__main__":

	query = c.execute('''SELECT * FROM crestronLiveSports''')

	liveSports = [dict(row) for row in query.fetchall()]


		#Write text file iis server for Crestron to read.
	with open(CRESTRON_LIVE_FILE,'w') as file:

			for i in liveSports:
				# remove sd channel no info
				del i['SDNo']

				event = i['event']
				event  = r'<FONT size=""30"" face=""Crestron Sans Pro"" color=""#ffffff"">'+event+'</FONT>'	
				line = [i['sport'],event,i['date'],i['startTime'],i['duration'],i['stopTime'],i['channelName'],i['HDNo'],'\n']
				newline = ','.join(str(i) for i in line)
				print newline
				file.write(newline)


	




# def getLiveSports(date,start,stop):

# 	sdchannels=['NHL Centre Ice 10','NBA League Pass 10']

# 	query = c.execute('''SELECT DISTINCT channelName,cast(HDNo as text),cast(SDNo as text),date,startTime,duration,sport,event
# 							 from liveSports 
# 							 where date = ?
# 							 and startTime between ? and ?''',(date,start,stop))

# 	sportslist = [dict(channelName=row[0],HDNo=row[1],SDNo=row[2],date=row[3],startTime=row[4],duration=row[5],sport=row[6],event=row[7]) for row in query.fetchall()]

# 	for i in sportslist:
		
# 		#add '0' to digital SD channels from sdchannels list
# 		if  i['channelName'] in sdchannels:
		
# 			i['SDNo'] = i['SDNo']+'0'
		
# 		#Remove '0' from analog channels e.g = 23 instead of 23.0
# 		if i['SDNo']:
# 			if i['SDNo'][-1] == '0' and i['channelName'] not in sdchannels:
				
# 				i['SDNo'] = i['SDNo'][0:-2]	

# 	sportslist = th.sort_by_time(sportslist)
# 	return sportslist



# def check_for_event(date):

# 	query = c.execute('''SELECT * FROM ucEventCalendar WHERE date = ?''',(date,))
# 	result = query.fetchone()

# 	if result:
# 		event_start = result[2]
# 		event = result[3]
# 		print event,event_start
# 		return event,event_start
# 	else:
		
# 		return False


# def sort_live_sports(team,sportslist):

# 	# checks to make sure team exists in event if not then defaults to other_sport for all Crestron data
# 	if team:

	
# 		if any (team in i['event'] for i in sportslist):
# 			print "team in event"
# 			uc_team = [i for i in sportslist if team in i['event']]
# 			# print uc_team
# 			sport = uc_team[0]['sport']

# 			uc_sport = [i for i in sportslist if i['sport'] == sport and team not in i['event']]
# 			# print uc_sport

# 			uc_other_sport = [i for i in sportslist if i['sport'] != sport and team not in i['event']]

# 			# print uc_other_sport

# 			uc_team = sorted(uc_team,key=lambda x:x['startTime'])
# 			uc_sport = sorted(uc_sport,key= lambda x:x['startTime'])
# 			other_sport = sorted(uc_other_sport,key=lambda x:x['sport'])

# 			crestron = uc_team + uc_sport + other_sport
# 			print "A"
# 			return crestron

# 		else:
# 			print "B"
# 			return sportslist


# 	else:
# 		print "C"
# 		return sportslist
		








	
	


			
			# for i in crestron:
			# 	# remove sd channel no info
			# 	del i['SDNo']

			# 	endtime = th.addTime(i['startTime'],i['duration'])
			# 	line = [i['sport'],i['event'],i['date'],i['startTime'],i['duration'],endtime,i['channelName'],i['HDNo'],'\n']
			# 	newline = ','.join(str(i) for i in line)
			# 	f.write(newline)



				







