from datetime import datetime ,timedelta,date
import time
from dateutil import tz

from_zone = tz.tzutc()
to_zone = tz.tzlocal()

def convert_utc_to_local(string):
	utc = datetime.strptime(string,"%Y-%m-%d %H:%M:%S")
	utc = utc.replace(tzinfo=from_zone)
	local = utc.astimezone(to_zone)
	local =  datetime.strftime(local,'%Y-%m-%d %H:%M:%S')
	return local

def convert_local_to_utc_ver2(string):
	local = datetime.strptime(string,"%Y-%m-%d %H:%M")
	local = local.replace(tzinfo=to_zone)
	utc = local.astimezone(from_zone)
	utc = datetime.strftime(utc,'%Y-%m-%d %H:%M:%S')
	return utc

def convert_local_to_utc(string):
	local = datetime.strptime(string,"%m/%d/%Y %I:%M %p")
	local = local.replace(tzinfo=to_zone)
	utc = local.astimezone(from_zone)
	utc = datetime.strftime(utc,'%Y-%m-%d %H:%M:%S')
	return utc

def format_time(string):
	timeobject = datetime.strptime(string,"%Y-%m-%d %H:%M:%S")
	date = datetime.strftime(timeobject,"%Y-%m-%d")
	time = datetime.strftime(timeobject,"%H:%M:%S")
	return date,time
	
def sort_by_time(query):
	for i in query:
		i['startTime']=datetime.strptime(i['startTime'],"%H:%M:%S")
	sortedlist = sorted(query,key=lambda key:key['startTime'])
	for i in sortedlist:
		i['startTime']= datetime.strftime(i['startTime'],"%I:%M %p")
	return sortedlist

def generic_start_stop_time(start,stop):
	today = datetime.date(datetime.today())
	today = datetime.strftime(today,"%m/%d/%Y") 
	start = today + " %s" % start
	stop = today + " %s" % stop
	return start,stop

def sevenDay_start_stop_time():
	startDate = datetime.date(datetime.today())
	stopDate = startDate + timedelta(days=7)

	startDate = datetime.strftime(startDate,"%m/%d/%Y") 
	
	stopDate = datetime.strftime(stopDate,"%m/%d/%Y")
	start = startDate + " 12:00 AM"
	stop = stopDate + " 11:59 PM" 
	
	return start,stop

def convert_date_string(date):
	date = datetime.strptime(date,"%m/%d/%Y")
	date = datetime.strftime(date,"%Y-%m-%d")
	return date

def convert_time_string(time):

	time = datetime.strptime(time,"%I:%M %p")
	time = datetime.strftime(time,"%H:%M:%S")
	return time


def date_today():
	return datetime.strftime(date.today(),"%Y-%m-%d")


def get_utc_start_end_times():

	start = '00:00'
	stop = '23:59'
	dates = [date.today() + timedelta(days=x) for x in range(1)]
	startTimes = [datetime.strftime(x,"%Y-%m-%d") +' '+ start for x in dates]
	stopTimes = [datetime.strftime(x,"%Y-%m-%d") +' '+ stop for x in dates]
	times =  zip(startTimes,stopTimes)
	utcStartEndTimes = [(convert_local_to_utc_ver2(i[0]),convert_local_to_utc_ver2(i[1]) ) for i in times]
	return utcStartEndTimes


def date_today_withMonth():
	return datetime.strftime(date.today(),"%Y-%b-%d")

def date_tomorrow():
	return datetime.strftime(date.today()+timedelta(days=1),"%Y-%m-%d")

def convert_to_am_pm(time):
	time = datetime.strptime(time,"%H:%M:%S")
	time = datetime.strftime(time,"%I:%M %p")
	return time

def now():
	return time.ctime()

def date_email():
	return datetime.strftime(date.today(),"%m-%d-%Y")


def addTime(startTime,duration):
	startTime = datetime.strptime(startTime,"%H:%M:%S")
	endTime = startTime + timedelta(minutes=duration)
	endTime = datetime.strftime(endTime,"%H:%M:%S")
	return endTime

def convert_to_24hr(time):

	time = datetime.strptime(time,"%I:%M %p")
	newtime = datetime.strftime(time,"%H:%M")
	return newtime







