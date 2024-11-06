from pymongo import MongoClient
import json

# MongoDB setup
client = MongoClient('mongodb://localhost:27017/')
db = client['dsa3101']
collection = db['inference_data']

with open('example_responses.json', 'r') as file:
    data = json.load(file).get('data')

result = collection.insert_one({
            'data': data,
            'name': 'test1'
        })

print(result)