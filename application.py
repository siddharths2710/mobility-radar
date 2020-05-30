"""
      __  __      ___     __      __      __  
 |\/|/  \|__)||   ||\ /__|__) /\ |  \ /\ |__) 
 |  |\__/|__)||___|| |   |  \/~~\|__//~~\|  \ 
                                              

The server-side logic for handling client requests, 
which should run as an Azure App service.
Ideally the template in the / endpoint fetches the
location and passes it to the /locations endpoint
for further processing
"""
from flask import Flask, redirect, render_template
import pickle5 as pickle
import sklearn.neighbors
import numpy as np
import geopy.distance
import geopy.geocoders
import azure.storage.blob
import pymongo

app = Flask(__name__)

vantage_pts = None
geolocator = None
mongo_client = None
ccodes = { "bounce": "#eb3b3b", "yulu": "#0077c7", "loca": "#4f0fd1", "vogo": "#e3d005", "shuttl": "#05e3b7" }

# Deserializer for the pickle file stored in BlobContainer
def read_vantage_pts_from_blob_container():
	blob_client = azure.storage.blob.BlobClient.from_connection_string(conn_str="DefaultEndpointsProtocol=https;AccountName=mobilityhack;AccountKey=TBq6mUKB1uT7SIBWxSbgSUPLKPjdlddLeNI/oLQRqHuEbdpRwXrV5IYbn+CFpOC65Dj67C8iRNwgSfU7ej6B5w==;EndpointSuffix=core.windows.net", container_name="vantage-pts-container", blob_name="vantage_pts_blob.pickle")
	blob_data = blob_client.download_blob()
	return pickle.loads( blob_data.readall() )

# Setter of region color code in map
def set_region_color_code(region):
	region['color'] = ccodes[region['service']]
	return region

# Primary endpoint that a device hits
@app.route("/")
def about():
	return render_template("index.html")

# Endpoint that serves the available mobility services based on location
# The KD-Tree for every service is queried against the provided location
# From which, the nearest location for each mobility service is derived
# Params: Latitude, Longitude
@app.route( "/locations/<latitude>/<longitude>" , methods=[ "GET" ] )
def process_location( latitude, longitude ):
	global vantage_pts
	global geolocator
	latitude, longitude = float(latitude), float(longitude)
	result = { "services": {}, "cur_location": { "address": "", "coordinates": { "latitude": latitude, "longitude": longitude } } }
	cur_location = [ latitude , longitude ]
	try:
		if vantage_pts is None:
			vantage_pts = read_vantage_pts_from_blob_container()
		if geolocator is None:
			geolocator = geopy.geocoders.Nominatim(user_agent="mobility_radar")
		try:
			result[ "cur_location" ][ "address" ] = geolocator.reverse( "{}, {}".format( latitude,longitude ) ).address
		except Exception as e:
			pass
		for service in vantage_pts:
			dist, index = vantage_pts[ service ][ 'tree' ].query( np.array( [ cur_location ] ) , k = 1 )
			idx = index[0][0]
			ltlng, radius  = vantage_pts[ service ][ "regions" ][ idx ]
			if geopy.distance.geodesic( cur_location, ltlng ).meters <= radius:
				result["services"][service] =  {}
				result["services"][service]["location"] = { "latitude": ltlng[0], "longitude": ltlng[1] }
				result["services"][service]["play_store_id"] = vantage_pts[service]['play_store_id']
				result["services"][service]["img_url"] = vantage_pts[service]['img_url']
		return render_template("loc.html", result=result )
	except Exception as e:
		raise e


@app.route( "/regions")
def show_regions():
	global mongo_client
	if mongo_client is None:
		mongo_client = pymongo.MongoClient("mongodb://mobility-vantage-pt-region:dW9VlngM8nxNiSdXy39KyUzkzuYFXYz9pMGkwLdzpSeZKm92PPkkZcdY83kBqUsb7g9robY4uXyP8Vs0EjPmqQ==@mobility-vantage-pt-region.mongo.cosmos.azure.com:10255/?retrywrites=false&ssl=true&replicaSet=globaldb&maxIdleTimeMS=120000&appName=@mobility-vantage-pt-region@")
	db = mongo_client.mobility_radar
	regions = list( map( set_region_color_code , db.regions.find() ) )
	
	return render_template("regions.html", data={'regions':regions,"ccodes":ccodes})

# Common Error Handlers
@app.errorhandler(404)
def page_not_found_handler(e):
	return "Endpoint Not Found"


@app.errorhandler(401)
def unauthorized_handler(e):
	return  "Unauthorized"


@app.errorhandler(403)
def forbidden_handler(e):
	return "Forbidden access"


@app.errorhandler(408)
def request_timeout_handler(e):
	return "Request Timeout"

@app.errorhandler(500)
def server_err_handler(e):
        return "Server Error"


if __name__ == "__main__":
	app.run()
