from datetime import datetime
from flask import Flask, request, Response
from pymongo import MongoClient
import argparse
import json

argParser = argparse.ArgumentParser()
argParser.add_argument("-id", "--id", type = int,  help="server id")
argParser.add_argument("-port", "--port", type = int,  help="port number")

server_id = None

app = Flask(__name__)
app.secret_key = "some_key"

client = MongoClient('localhost', 27017)
mongo_db = client.flask_db
orders = mongo_db.orders

@app.route('/orders/add', methods=['POST'])
def add_order():
    if 'user_id' not in request.json or 'products' not in request.json:
        return Response(json.dumps({"status" : 422}), mimetype='application/json')

    req = json.loads(request.json)
    orders.insert_one({'user_id' : req['user_id'], 'products' : req['products'], 'date' : datetime.now(), 'status' : "pending"})
    
    return Response(json.dumps({"status" : 200}), mimetype='application/json')

if __name__ == "__main__":
    args = argParser.parse_args()
    if args.id == None or args.port == None:
        print("Please specify server id and port")
        exit()
    
    server_id = args.id
    app.run(port = args.port)