import pymongo
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
myclient.drop_database("mydatabase")
mydb = myclient["mydatabase"]
mycol_sources=mydb["sources"]