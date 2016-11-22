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
		
		utils.get_lineup_listings(ALL_DAY_START,DAY_STOP,TODAY,config.LINEUPS,cursor)
		print "Got Lineup Listings"
		utils.make_infocaster_file(ALL_DAY_START,DAY_STOP,TODAY,cursor)
		print "Made ALL_DAY Infocaster text file"
		# utils.update_crestron_live_sports_db(conn)
		# print "Updated Crestron db"
		utils.make_crestron_live_sports_file(TODAY,cursor)
		print "Updated Crestron TXT file"

	except Exception as e:
		print "Get Lineups Listings failed with error: %s" % e

def do_it_late(start_time):
	try:
		utils.make_infocaster_file(HALF_DAY_START,DAY_STOP,TODAY,cursor)
		print "Made half-day infocaster text file"
	except Exception as e:
		print "Make infocaster hald day failed with error: %s" % e

def auto():

	 	try:
	 		print "Checking Time"
			if dt.now().hour == 18:

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

		
