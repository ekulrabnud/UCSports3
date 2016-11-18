import sevenDaySchedule as sds
import make_infocastertxt_sports_for_today as misft
from datetime import datetime as dt
import time
import timehandler as th
import datetime
import config
import argparse
import makeCrestronLiveSports
import utils
import sqlite3

conn = sqlite3.connect('uctvDb')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

ALL_DAY_START = config.INFOCAST_ALL_DAY_START 
HALF_DAY_START= config.INFOCAST_HALF_DAY_START 
DAY_STOP = config.INFOCAST_DAY_STOP

TODAY = th.date_today()
DATE = "2015-03-11"
TOMOROW = th.date_tomorrow()

parser = argparse.ArgumentParser(description='Operate Sports Listings')
parser.add_argument('-update',action="store_true", help='update database')
args = parser.parse_args()

def do_it_early(start_time):
	
	try:
		start,stop = th.sevenDay_start_stop_time()
		
		sds.get_lineup_listings()
		print "Got Api Listings"
		misft.make_text_file(th.date_today(),start_time,DAY_STOP)
		print "Updated Infocaster File"
		utils.update_crestron_live_sports_db(conn)
		print "Updated Crestron db"
		utils.make_crestron_live_sports_file(conn,TODAY)
		print "Updated Crestron TXT file"

	except Exception as e:
		print e.args

def do_it_late(start_time):
	try:
		misft.make_text_file(th.date_today(),start_time,DAY_STOP)
	except:
		print "do_it_late failed"

def auto():

	 	try:
	 		print "Checking Time"
			if dt.now().hour == 3:

				do_it_early(ALL_DAY_START)
				print "FullDay"

			elif dt.now().hour == 15:
				do_it_late(HALF_DAY_START)	
				print "HALF DAY"
	 	except Exception as e:
	 		print "problem %s" % e
	

if __name__ == '__main__':

	if args.update:
		
		do_it_early(ALL_DAY_START)
	else:
		auto()

		
