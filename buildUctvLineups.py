import sqlite3
from tvMediaApi_dev import TvMedia
import config



 
api = TvMedia(config.APIKEY,config.BASE_URL)

# print api.lineups('60302')

print api.lineup_details(92039)


# api.trace_out = 1
# # api.lineups("60302")
# listings = api.lineup_listings("41614D")
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




