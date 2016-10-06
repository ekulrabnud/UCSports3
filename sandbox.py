import utils
import timehandler as th
import sqlite3

conn = sqlite3.connect('uctvDb')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()
DATETODAY = th.date_today()



# print utils.check_for_event(DATETODAY,cursor)
# utils.make_crestron_live_sports_file()
utils.update_crestron_live_sports_db()