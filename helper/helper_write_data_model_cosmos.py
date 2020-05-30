import pymongo
"""
Helper script to populate the below locations
into the collection defined in Azure Cosmos DB
Ideally we would manually place the region data
for a given service in Cosmos DB in the required format

If a new region is made available for a service, the
corresponding document that is added in Cosmos DB is
of the form

{
	"service": name in string
	"latitude": float
	"longitude": float
	"radius": int in meters
}

"""
"""
Vantage Points Schema: 
 
{
	'mobility service name': {
		[ lat, lng ]: radius ( in meters )
	}
}
"""
vantage_pts = \
{
	'loca': {
		'regions': {
			# Metro + Linked
			( 12.978219, 77.638563 ) : 1500, # Indiranagar
			( 12.973175, 77.635869 ) : 500,
			( 12.976232, 77.636325 ) : 500,
			( 12.975751, 77.641073 ) : 500,
			( 12.967502, 77.641416 ) : 500,
			( 12.962705, 77.641653 ) : 500,
			( 12.957852, 77.641207 ) : 500,
			( 12.954165, 77.641177 ) : 500,
			( 12.951825, 77.639665 ) : 500,  # EGL
			( 12.949863, 77.642139 ) : 500,
			( 12.950564, 77.642772 ) : 500,
			( 12.947917, 77.646367 ) : 500,
			

			( 12.990934, 77.652635 ) : 1500, # Baiyyappanahalli
			( 12.986946, 77.648191 ) : 1500,
			( 12.896027, 77.569986 ) : 1500, # Yelachenahalli
			( 12.907734, 77.572986 ) : 1500, # JP Nagar
			( 12.933224, 77.588388 ) : 1500, # Jayanagar
			( 12.971092, 77.537321 ) : 1000, # Vijaynagar
			( 12.952468, 77.537238 ) : 1000  # Mysore Road
		}
		

	},
	'yulu': {
		"regions": {
			( 12.978219, 77.638563 ) : 1500, # Indiranagar
			( 12.951825, 77.639665 ) : 500,
			( 12.947917, 77.646367 ) : 500,
			( 12.962705, 77.641653 ) : 500,
			( 12.975751, 77.641073 ) : 500,

			( 12.976003, 77.591607 ) : 2000, # Cubbon Park

			( 12.923107, 77.640098 ) : 10000, # HSR
			( 12.952819, 77.700850 ) : 10000,  # Marathahalli
			(  12.935032, 77.623266 ) : 10000, # Koramangala
			(  12.916534, 77.608813 ) : 10000, # BTM
			(  12.952732, 77.577082 ) : 2000, # Sajjan Rao Circle
			(  12.952732, 77.577082 ) : 1000, # Lalbagh
			(  12.969669, 77.741768 ) : 10000 # Whitefield
		}
		
	},

	'bounce': {
		"regions": {
			( 12.976003, 77.591607 ): 50000
		}
	}
}

if __name__ == "__main__":
	client = pymongo.MongoClient("mongodb://mobility-vantage-pt-region:dW9VlngM8nxNiSdXy39KyUzkzuYFXYz9pMGkwLdzpSeZKm92PPkkZcdY83kBqUsb7g9robY4uXyP8Vs0EjPmqQ==@mobility-vantage-pt-region.mongo.cosmos.azure.com:10255/?retrywrites=false&ssl=true&replicaSet=globaldb&maxIdleTimeMS=120000&appName=@mobility-vantage-pt-region@")
	db = client.mobility_radar
	for service in vantage_pts:
		regions = vantage_pts[ service ]["regions"]
		for region in regions:
			area = {}
			area['latitude'] = region[0]
			area['longitude'] = region[1]
			area['radius'] = regions[region]
			area['service'] = service
			if bool(db.regions.count_documents({ "latitude": area["latitude"], "longitude": area["longitude"] })):
				db.regions.remove({ "latitude": area["latitude"], "longitude": area["longitude"] })
			db.regions.insert_one(area)