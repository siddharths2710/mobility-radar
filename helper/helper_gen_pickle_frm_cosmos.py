"""
Helper script to populate the BlobContainer with the pickle file  containing
* List of regions available for a given service
* the KD-tree object for each service ( used for fast lookups of nearby locations )
* The metada associated with the service
	* play store id
	* image uri
"""
import json
import pymongo
import numpy as np
import sklearn.neighbors
import pickle5 as pickle
import azure.storage.blob


meta = {
	'play_store_id': {
		'yulu': 'app.yulu.bike',
		'loca': 'com.locarides.microtransit',
		'bounce': 'com.metrobikes.app',
		'vogo': 'com.VoDrive',
		'shuttl': 'app.goplus.in.myapplication'
	},
	'img_url': {
		'yulu': 'https://lh3.googleusercontent.com/mo8urT34ZqGYR_nIUdJyZ64N3ePNpvIgOIvE2QwAwYl8P6MGQtJL5V1-EUVw3LcZQakw',
		'loca': 'https://lh3.googleusercontent.com/jFOzcmU116HJJa2p_KS-6h4yB6A67HAyoChp6qF_PSwWQIzqPJvE4XSzDhPZObjCGg',
		'bounce': 'https://res-3.cloudinary.com/crunchbase-production/image/upload/c_lpad,h_256,w_256,f_auto,q_auto:eco/e0jspdelenxnx6hf5j4d',
		'vogo': 'https://res-3.cloudinary.com/crunchbase-production/image/upload/c_lpad,h_256,w_256,f_auto,q_auto:eco/e0jspdelenxnx6hf5j4d',
		'shuttl': 'https://lh3.googleusercontent.com/rbMbfidDUKWooC3ykpRsPIHAp2eQWjL7giPkx1UEG0XqecqFFPT9R5AmiNtE0-8I2UA=s180'
	}
}

"""
Generator of K-D Tree for every update to data model
"""

if __name__ == "__main__":

	vantage_pts = {}
	region_list = {}
	client = pymongo.MongoClient("my_mongo_client")
	db = client.mobility_radar
	for entry in db.regions.find():
		service = entry['service']
		if service not in vantage_pts:
			vantage_pts[ service ] = {}
			region_list[ service ] = []
		region_list[ service ].append( [ ( entry["latitude"], entry["longitude"] ), entry['radius'] ] ) 
	
	for service in vantage_pts:
		vantage_pts[ service ][ "regions" ] = region_list[ service ]
		vantage_pts[ service ][ 'tree' ] = sklearn.neighbors.KDTree( np.array( list( map( lambda x: x[0], region_list[ service ] ) ) ), leaf_size = 2 )
		vantage_pts[ service ][ 'play_store_id' ] = meta['play_store_id'][ service ]
		vantage_pts[ service ][ 'img_url' ] = meta['img_url'][ service ]


	blob_client = azure.storage.blob.BlobClient.from_connection_string(conn_str="my_conn_str", container_name="vantage-pts-container", blob_name="vantage_pts_blob.pickle")
	blob_client.upload_blob(pickle.dumps( vantage_pts ) , overwrite = True )