import requests
import hashlib
import json
import pickle
import time
import timehandler as th


class API(object):

    URL =	'http://api.tvmedia.ca/tv/v4/' 

    LINEUPIDCHICAGO = "41614D"
    LINEUPIDCHICAGOOTA = "21094"
    LINEUPIDMONTREAL = "41487"

    STATIONLOGO = 'http://developer.tvmedia.ca/images/stations/size/'
    TEAMLOGO =  'http://developer.tvmedia.ca/images/league/'

    def __init__(self,api_key):

        self.api_key = api_key
        self.chicago_lineup_channels = None
        self.chicago_lineup_channels_OTA = None
        self.montreal_lineup_channels = None
        self.sports = None
  
    def get_lineupsByID(self):

        print "getting lineups"
        url = self.URL + 'lineups/' + self.LINEUPIDCHICAGO
        params = {"api_key":self.api_key}
        r = requests.get(url,params=params)
        self.chicago_lineup_channels = json.loads(r.content)

        url = self.URL + 'lineups/' + self.LINEUPIDCHICAGOOTA
        params = {"api_key":self.api_key}
        r = requests.get(url,params=params)
        self.chicago_lineup_channels_OTA = json.loads(r.content)

        url = self.URL + 'lineups/' + self.LINEUPIDMONTREAL
        params = {"api_key":self.api_key}
        r = requests.get(url,params=params)
        self.montreal_lineup_channels = json.loads(r.content)

    def get_sport(self,start,stop,requestData):
        
        start = th.convert_local_to_utc(start)
        stop = th.convert_local_to_utc(stop)
        
        for lineupID, stations in requestData.items():
            try:
                url = self.URL + 'lineups/' + lineupID + '/listings/grid'
                params = {"api_key":self.api_key,"start":start,"end":stop,"station":stations,"sportEventsOnly":1}
                r = requests.get(url,params=params)
                yield json.loads(r.content)
            except Exception as e:
                yield e





    def start(self,start):
        return th.convert_local_to_utc(start)

    def stop(self,stop):
        return th.convert_local_to_utc(stop)


    def archive(self,name):
        f = open(name,'wb')
        pickle.dump(self,f)
        f.close()




