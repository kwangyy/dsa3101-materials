from pymongo import MongoClient

client = MongoClient('mongodb://localhost:27017/')
db = client['email']
collection = db['email_ground_truth_prediction']

kg = collection.find_one({"name": "test"})

for json in kg["data"]["relationships"]:
    print(json)