from flask import Flask, request, session, g, redirect, url_for, render_template, flash,jsonify
import config
import sqlite3
import timehandler as th
import sevenDaySchedule as sds
import make_infocastertxt_sports_for_today as misft
import pdfkit
import utils
import json

from tvMediaApi_dev import TvMedia

app = Flask(__name__)
app.config.from_object(config)

START = config.DEFAULT_START
STOP = config.DEFAULT_STOP
DATETODAY = th.date_today()

api = TvMedia(config.APIKEY,config.BASE_URL)

def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

@app.before_request
def before_request():
	g.db = connect_db()

@app.teardown_request
def teardown_request(exception):
	db = getattr(g, 'db', None)
	if db is not None:
		db.close()

#Error******************************************************************************************************
@app.errorhandler(404)
def page_not_found(error):
    return redirect(url_for('index'))

# Index  ******************************************************************************************************
@app.route('/')
def index():
	
	return render_template('index.html')


# Channel Guide **********************************************************************************************
@app.route('/channelGuide',methods=['GET','POST'])
def channelGuide():

	if request.method == 'GET':
	
		channels = utils.getChannels(g.db)

	elif request.method == 'POST':
		
		columnName = request.form['columnName']
		rowid = request.form['id']
		value = request.form[columnName]

		utils.updateUctvLineups(columnName,rowid,value)

		return jsonify(error=0,message="Database changes saved")
      
	return render_template('Guides/channelGuide.html',channels=channels)


# Live Sports Schedule **********************************************************************************************
@app.route('/liveSports',methods=['GET','POST'])
def liveSports():

	if request.method == 'GET':

		sportslist = utils.getLiveSports(DATETODAY,START,STOP,g.db)
	
		return render_template('LiveSports/liveSports.html',sportslist=sportslist,request=request)

	#submit new date time range for query
	elif request.method == 'POST':
		
		date = th.convert_date_string(request.form['date'])
		start = th.convert_time_string(request.form['start'])
		stop = th.convert_time_string(request.form['stop']) 
		sportslist = utils.getLiveSports(date,start,stop,g.db)


		
		return render_template('LiveSports/liveSportsTable.html',sportslist=sportslist,request=request)

@app.route('/editLiveSports',methods=['GET','POST'])
def edit():
	


	sportslist = utils.getLiveSportsWithId(DATETODAY,START,STOP,g.db)
	
	return render_template('LiveSports/liveSportsEdit.html',sportslist=sportslist)

@app.route('/saveLiveSportsEdit',methods=['POST'])
def save():

		try:
			for id,row in request.form.iterlists():
		
				#this filters form data so that we ignore unwanted data
				#len == 5 make sure delete's are ignored
				if len(row) > 1:
					#converts time to 24 hour clock
					row[1] = th.convert_time_string(row[1])
					#adds id to end of row list
					row.append(id)
					g.db.execute('''UPDATE liveSports SET event=?,startTime=?,channelName=?,HDNo=?,SDNo=? 
					WHERE id = ?''',row)

			deletions = [(int(i),) for i in request.form.getlist('delete')]
			g.db.executemany('''DELETE from liveSports where id = ?''',deletions)
			g.db.commit()
		
			sportslist = utils.getLiveSports(DATETODAY,START,STOP,g.db	)

		
			response = render_template('LiveSports/liveSportsTable.html',sportslist=sportslist)
			return jsonify(html=response,error=0,message="Live Sports Updated");

		except sqlite3.Error,e:

			return jsonify(error=1,message="Error!! %s" % e.args[0]) 



# Crestron Live Sports **********************************************************************************************
@app.route('/crestronLiveSports')
def crestronLiveSports():
	
	liveSports = utils.getCrestronLiveSports(g.db)
	event = utils.check_for_event(th.date_today(),g.db);
	print DATETODAY,event

	return render_template('LiveSports/crestronLiveSports.html',liveSports=liveSports,event=event)
	
@app.route('/editCrestronLiveSports',methods=['GET','POST'])
def editCrestronLiveSports():

	if request.method == 'GET':

	
		liveSports = utils.getCrestronLiveSports(g.db)

		return render_template('LiveSports/crestronLiveSportsEdit.html',liveSports=liveSports,event='test')

	try:

		#hack to get delete thing working
		for id,row in request.form.iterlists():
			if id == 'delete':
				continue
		
	 		row.append(id)
	 	
	 		g.db.execute('''UPDATE crestronLiveSports 
	 				SET sport=?,
	 					event=?,
	 					date=?,
	 					startTime=?,
	 					duration=?,
	 					stopTime=?,
	 					channelName=?,
	 					uctvNo=?
	 					WHERE id = ?''',row)


	 	deletions = [(int(i),) for i in request.form.getlist('delete')]
	 	print request.form.getlist('delete')
		g.db.executemany('''DELETE from crestronliveSports where id = ?''',deletions)
		g.db.commit()

	except Exception as e:
		
		return jsonify(error=1,message="Error!! %s" % e.args[0]) 

	liveSports = utils.getCrestronLiveSports(g.db)

	return render_template('LiveSports/crestronLiveSportsTable.html',liveSports=liveSports)
		
@app.route('/crestronLiveSportsReload')
def reload():
	print g.db
	utils.update_crestron_live_sports_db(g.db)

	liveSports = utils.getCrestronLiveSports(g.db)

	return render_template('LiveSports/crestronLiveSportsEdit.html',liveSports=liveSports,event='test')


@app.route('/crestronLiveSportsUpdate')
def crestronLiveSportsUpdate():

	
	# try:
	# 	utils.make_crestron_live_sports_file(g.db)
	# 	liveSports = utils.getCrestronLiveSports(g.db)
	# 	return jsonify(error=0,message="Successfully updated Crestron Live Sports Text File")
	# except Exception as e:
	# 	print "error"
	# 	return jsonify(error=1,message="Error!! %s" % e.args[0]) 

	utils.make_crestron_live_sports_file(g.db)
	liveSports = utils.getCrestronLiveSports(g.db)
	# 	return jsonify(error=0,message="Successfully updated Crestron Live Sports Text File")

	return render_template('LiveSports/crestronLiveSportsTable.html',liveSports=liveSports,event="test")


# Channel Lineup**********************************************************************************************
@app.route('/lineups',methods=['GET','POST'])
def channelLineup():

	if request.method == 'GET':
		query= g.db.execute('''SELECT * from uctvLineups ''')
		channelLineups = [dict(row) for row in query.fetchall()]
		return render_template('Lineups/channelLineups.html',channelLineups=channelLineups)


	for i in request.form.getlist('edits[]'):
		row = json.loads(i)
		col = row['col']
		val = row['value']
		id = row['id']
		g.db.execute('UPDATE uctvlineups SET ' + col + ' = ? WHERE id = ?',(val,id))
	g.db.commit()
		

	
		
		

	query= g.db.execute('''select * from uctvLineups ''')
	channelLineups = [dict(row) for row in query.fetchall()]
	return render_template('Lineups/channelLineups.html',channelLineups=channelLineups)


	
# Sports Lineup **********************************************************************************************
@app.route('/sportsLineup',methods=['GET','POST'])
def sportsLineup():

	if request.method == 'GET':

		query = c.execute('select * from uctvLineupsSport')
		sportsLineup = [dict(id=row[0], chName=row[1], lineupID=row[2], hdStationID=row[3], uctvHDNo=row[4],uctvSDNo=row[5],origHDChNo=row[6]) for row in query.fetchall() ]
		
		return render_template('sportsLineup.html',sportsLineup=sportsLineup)

# Documentation **********************************************************************************************
@app.route('/docs')
def docs():

	return render_template('Docs/docs.html')

# Email. Formats email **********************************************************************************************
@app.route('/email',methods=['GET','POST'])
def email():

	if request.method == 'GET':

		sportslist = getLiveSports(DATETODAY,START,STOP)

	else:

		date = th.convert_date_string(request.form['date'])
		start = th.convert_time_string(request.form['start'])
		stop = th.convert_time_string(request.form['stop']) 

		sportslist = utils.getLiveSports(date,start,stop,g.db)
	
	return render_template('LiveSports/email.html',sportslist=sportslist,date=request.form['date'])

#Publishes infocaster text file **********************************************************************************************
@app.route('/infocast',methods=['POST'])
def publish_infocast():

	try:
		formDate = th.convert_date_string(request.form['date'])
		formStart = th.convert_time_string(request.form['start'])
		formStop = th.convert_time_string(request.form['stop']) 

		misft.make_text_file(formDate,formStart,formStop)

		return jsonify(error=0,message="Infocaster Text File Updated at %s\\%s" % (config.DIR_INFOCASTER_TEXT,"uctvSportsSchedule.txt"))

	except Exception as e:

		return jsonify(error=1,message="Publish Infocast failed!!!: %s" % e.args[0])

@app.route('/add',methods=['GET','POST'])
def add():
	try:
		r = request.form
		date = th.date_today()
		time = th.convert_time_string(r['time'])
		row = [r['channel'],r['hd'],r['sd'],date,time,r['event'],r['sport']]
		c.execute('''INSERT INTO liveSports (channelName,HDNo,SDNo,date,startTime,event,sport)
						VALUES (?,?,?,?,?,?,?)''',row)

		conn.commit()

		return jsonify(error=0,message="Event added to Database")

	except Exception as e:
		# return jsonify(error=1,message="Publish Infocast failed!!!: %s" % e.args[0])
		return e.args[0]
	
# Reload database from API **********************************************************************************************
@app.route('/reloadSports')
def reloadSports():

	try: 
		start,stop = th.sevenDay_start_stop_time()
		sds.get_sport_listings(start,stop)
		sportslist = utils.getLiveSports(DATETODAY,START,STOP,g.db)
	
	
		return render_template('LiveSports/liveSportsTable.html',sportslist=sportslist)
	except Exception as e:
		return jsonify(error=1,message="Reload failed!!! %s" % e.args[0])
 		
# Make a PDF ***********************************************************************************************************
@app.route('/pdf',methods=['POST'])
def pdf():
	pdfconfig = pdfkit.configuration(wkhtmltopdf=config.EXE_WKHTMLTOPDF)

	pdf_options = {
	'page-width':'1.5in',
    'page-size': 'Letter',
    'margin-top': '0.75in',
    'margin-right': '0.75in',
    'margin-bottom': '0.75in',
    'margin-left': '1.0in',
    'encoding': "UTF-8",
    'no-outline': None
	}
               
	pdf_filename = 'UCTV Sports Schedule '+ request.json['date'].replace('/','-') +'.pdf'
	
	out_pdf = config.DIR_SPORTS_PDF + '\\' + pdf_filename

	css ='''<style> table,th,td{
    border:1px solid black;
    border-collapse: collapse;
    font-family: Arial;
    font-size: 11pt;}

    table{width:800px;}

    input{border:0px;}
	
    h3{border:0px;font-family:Arial;font-size:20pt;}
    .pdf_no_show{display:none;}
  
    tr.pdf input[type="text"],tr.pdf td{background-color:FCAE1C;} 

    th{background-color:#7AABEB;}
    td{padding:2px;}</style>\n'''

	with open("pdf.html",'wb') as f:
		f.write(css)
		f.write(request.json['page'].encode('utf-8'))

	pdfkit.from_file('pdf.html', out_pdf,configuration=pdfconfig,options=pdf_options)

	return "Successfully created %s" % out_pdf

@app.route('/findLineup',methods=['POST'])
def addLineup():

		zipcode = request.form['zipcode']
		
		lineups = api.lineups(zipcode)
		
		return render_template('Lineups/availableLineups.html',lineups=lineups)

@app.route('/sandbox')
def sandbox():

	return render_template('sandbox/sandbox.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5005)