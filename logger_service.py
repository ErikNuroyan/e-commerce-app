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
responses = mongo_db.responses

@app.route('/log', methods=['POST'])
def log():
    if 'server_id' not in request.json or 'request' not in request.json:
        return Response(json.dumps({"status" : 422}), mimetype='application/json')

    dt = datetime.now()
    req = json.loads(request.json)
    responses.insert_one({'server_id' : req['server_id'], 'request' : req['request'], 'date' : dt})
    
    return Response(json.dumps({"status" : 200}), mimetype='application/json')

if __name__ == "__main__":
    args = argParser.parse_args()
    if args.id == None or args.port == None:
        print("Please specify server id and port")
        exit()
    
    server_id = args.id
    app.run(port = args.port)