import requests
import json
import time
import timehandler as th
import config




class TvMedia(object):

    max_get_retries = 1
    trace_out = True
    retry_delay = 1

    def __init__(self,api_key,base_url):

        self.api_key = api_key
        self.base_url = base_url

        # if isinstance(requests_session, requests.Session):
        #     self._session = requests_session
        # else:
        #     if requests_session:  # Build a new session.
        #         self._session = requests.Session()
        #     else:  # Use the Requests API module as a "session".
        #         from requests import api
        #         self._session = api

    def _internal_call(self,method,url,params=None):
        
        if params == None:
            params = {}

        url = self.base_url + url
     

        params['api_key'] = self.api_key

        #remove any kwargs that=None
        for k,v in params.items():
            if not v:
                params.pop(k)

        
     
        # if self.trace_out:
        #     print url,params

        r = requests.request(method,url,params=params)

        # if self.trace_out:
        #     print  ('http status',r.status_code)
        #     print (method,r.url)
           
        # print r.headers
        try:
            r.raise_for_status()
        except:
            if r.text and len(r.text)> 0 and r.text != 'null':
                print "error handler needed"
            else:
                print "error handler needed"
        finally:
            r.connection.close()

        if r.text and len(r.text) > 0 and r.text != 'null':
            if self.trace_out:
                # print('Response',r.content)
                return json.loads(r.content)
            else:
                return None


    def _get(self,url,params=None):

        retries = self.max_get_retries
        delay = self.retry_delay
        while retries > 0:
            try:
                return self._internal_call('GET',url,params)
            except Exception as e:
                time.sleep(delay)
                retries -= 1
                print "Error = %s" % str(e)

    def lineups(self,postalCode):

        url = 'lineups'
        params = {}
        params['postalCode'] = postalCode
        return self._get(url,params)

    def lineup_details(self,lineupID,userid=None):

        url = 'lineups/%s' % lineupID
      
        return self._get(url)

    def lineup_listings(self,lineupID,
                        start=None,
                        end=None,
                        channel=None,
                        station=None,
                        search=None,
                        sporttype=None,
                        league=None,
                        team=None,
                        sportEventsOnly=0,
                        liveOnly=0,
                        exclude=None,
                        ):

        url = 'lineups/%s/listings' % lineupID
        #Builtin locals function builds params dict from kwargs :-)
        params = locals()
        params.pop('self')
        params.pop('lineupID')
        params.pop('url')
        print url,params
        return self._get(url,params)

    def station_details(self,stationID):

        url = 'stations/%s' % stationID
        params = {}
        return self._get(url,params)



 
# api = TvMedia(config.APIKEY,config.BASE_URL)
# # api.trace_out = 1
# print (api.lineup_details(92039)).keys()
# listings = api.lineup_listings("41614D",search="Chicago Cubs")
# print type(listings)

# for i in listings:
#     for f in i.items():
#         print f[0],f[1]




# for i in listings:
#     print i['callsign'],i['inProgress']

# station = api.station_details("4186")

# print station['logoFilename']




# for i in listings:
#     if isinstance(i,dict):
#         for k,v in i.items():
#             print k








    # def requester(self,url,params):

    #     params["api_key"] = self.api_key
    #     print url,params
    #     response = requests.get(url,params=params)
      
    #     return json.loads(response.content)

    # def get_lineups_by_zip(self,zipcode):

    #     url = self.URL + "lineups"
    #     params = {"postalCode":zipcode}
    #     return self.requester(url,params)

  
    # def get_lineup(self,lineupId):

    #     url = self.URL + "lineups/" + lineupId
    #     params = {}
    #     _json =self.requester(url,params)

        
    #     return _json


    # def get_sport(self,start,stop,requestData):
        
    #     start = th.convert_local_to_utc(start)
    #     stop = th.convert_local_to_utc(stop)
        
    #     for lineupID, stations in requestData.items():
    #         try:
    #             url = self.URL + 'lineups/' + lineupID + '/listings/grid'
    #             params = {"api_key":self.api_key,"start":start,"end":stop,"station":stations,"sportEventsOnly":1}
    #             r = requests.get(url,params=params)
    #             yield json.loads(r.content)
    #         except Exception as e:
    #             yield e





    # def start(self,start):
    #     return th.convert_local_to_utc(start)

    # def stop(self,stop):
    #     return th.convert_local_to_utc(stop)


    # def archive(self,name):
    #     f = open(name,'wb')
    #     pickle.dump(self,f)
    #     f.close()




# # print type(api.get_lineups_by_zip(37385))
# # print type(api.get_lineup("8888"))
# json_print(api.get_lineups_by_zip(37385))
# json_print(api.get_lineup("88888"))




















































# def json_print(json_response):

#     if isinstance(json_response,list):

#         for i in json_response:
#             print json.dumps(i,sort_keys=False,separators=(',',':'))

#     elif isinstance(json_response,dict):

#         for k,v in json_response.items():
#             print k,v

