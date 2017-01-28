from tvMediaApi_dev import TvMedia
import config
api = TvMedia(config.APIKEY,config.BASE_URL)


zip = 60612


for i in api.lineups(zip):
	print i['providerName'],i['lineupID'],i['serviceArea']
