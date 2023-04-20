from datetime import datetime
from flask import Flask, jsonify, request, Response
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager, unset_jwt_cookies
from redis import Redis
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
import argparse
import json
import requests

argParser = argparse.ArgumentParser()
argParser.add_argument("-id", "--id", type = int,  help="server id")
argParser.add_argument("-port", "--port", type = int,  help="port number")

server_id = None

app = Flask(__name__)
app.secret_key = "some_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///items.sqllite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

redis_client = Redis(host='localhost', port=6379, db=0)

jwt = JWTManager(app)

client = MongoClient('localhost', 27017)
mongo_db = client.flask_db
sessions = mongo_db.sessions

db = SQLAlchemy(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(320), nullable=False, unique=True)
    name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    password = db.Column(db.String(120), nullable=False)
    
    def __init__(self, email, name, phone_number, address, password):
        self.email = email
        self.name = name
        self.phone_number = phone_number
        self.address = address
        self.password = generate_password_hash(password)
    
    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password,password)

def print_and_log(request_string, request_headers):
    dt = datetime.now()
    print('Server id: ', server_id, ' Request: ', request_string, ' Date: ', dt)

    # Send a request to logger service
    url = 'http://127.0.0.1:5004/log'
    headers = {k:v for k,v in request_headers}
    response = requests.post(url = url, json = json.dumps({"server_id" : server_id, "request" : request_string}), headers=headers).json()

    # We shouldn't return error code to the client because of the logger error    
    if response['status'] != 200:
        print("Error in the logger service!")

def populate_users_cache():
    users = User.query.all()
    cached_users = []
    for user in users:
        cached_users.append({"id": user.id, "email": user.email, "name": user.name, "password": user.password})
    redis_client.set('users', json.dumps(cached_users))

@app.route('/user/card_products')
@jwt_required()
def get_card_products():
    print_and_log('/card_products', request.headers)
    
    user_mail = get_jwt_identity()
    cached_users = redis_client.get('users')
    if not cached_users:
        print('Populating the cache of users')
        populate_users_cache()
    
    cached_users = json.loads(redis_client.get('users'))
    user_id = None
    for user in cached_users:
        if user['email'] == user_mail:
            user_id = user['id']
            break
    
    if user_id is None:
        return Response(json.dumps({"status": 401, "message": "User not logged in"}),  mimetype='application/json')
    
    user_session = sessions.find_one({'user_id': user_id})

    if user_session is None:
        return Response(json.dumps({"status": 401, "message": "User not logged in"}),  mimetype='application/json')
    
    return Response(json.dumps({"card_products": user_session["card_products"], "status": 200}),  mimetype='application/json')

@app.route('/user/add_to_card', methods=['POST'])
@jwt_required()
def add_to_card():
    print_and_log('/add_to_card', request.headers)
    
    user_mail = get_jwt_identity()
    cached_users = redis_client.get('users')
    if not cached_users:
        print('Populating the cache of users')
        populate_users_cache()
    
    cached_users = json.loads(redis_client.get('users'))
    user_id = None
    for user in cached_users:
        if user['email'] == user_mail:
            user_id = user['id']
            break
    
    if user_id is None:
        return Response(json.dumps({"status": 401, "message": "User not logged in"}),  mimetype='application/json')
    
    user_session = sessions.find_one({'user_id': user_id})

    if user_session is None:
        return Response(json.dumps({"status": 401, "message": "User not logged in"}),  mimetype='application/json')
    
    if 'item_id' in request.json:
        # Send a request to products service to validate item id
        url = 'http://127.0.0.1:5000/products/validate_item'
        headers = {k:v for k,v in request.headers}
        response = requests.get(url = url, data = json.dumps({"item_id" : request.json['item_id']}),headers=headers).json()

        if not response["is_valid"]:
            return Response(json.dumps({"status": 422, "message": "Wrong Input"}),  mimetype='application/json')
    else:
        return Response(json.dumps({"status": 422, "message": "Wrong Input"}),  mimetype='application/json')

    sessions.update_one({'user_id': user_id}, {"$push": { "card_products": request.json['item_id']} })
    
    return Response(json.dumps({"status": 200, "message": "Added to the card"}),  mimetype='application/json')

@app.route('/user/remove_from_card', methods=['POST'])
@jwt_required()
def remove_from_card():
    print_and_log('/remove_from_card', request.headers)

    user_mail = get_jwt_identity()
    cached_users = redis_client.get('users')
    if not cached_users:
        print('Populating the cache of users')
        populate_users_cache()
    
    cached_users = json.loads(redis_client.get('users'))
    user_id = None
    for user in cached_users:
        if user['email'] == user_mail:
            user_id = user['id']
            break
    
    if user_id is None:
        return Response(json.dumps({"status": 401, "message": "User not logged in"}),  mimetype='application/json')
    
    user_session = sessions.find_one({'user_id': user_id})

    if user_session is None:
        return Response(json.dumps({"status": 401, "message": "Session expired"}),  mimetype='application/json')

    if 'item_id' in request.json:
        # Send a request to products service to validate item id
        url = 'http://127.0.0.1:5000/products/validate_item'
        headers = {k:v for k,v in request.headers}
        response = requests.get(url = url, data = json.dumps({"item_id" : request.json['item_id']}),headers=headers).json()

        if not response["is_valid"]:
            return Response(json.dumps({"status": 422, "message": "Wrong Input"}),  mimetype='application/json')
    else:
        return Response(json.dumps({"status": 422, "message": "Wrong Input"}),  mimetype='application/json')

    sessions.update_one({'user_id': user_id}, {"$pull": { "card_products": request.json['item_id']} })
    
    return Response(json.dumps({"status": 200, "message": "Removed from the card"}),  mimetype='application/json')

@app.route('/user/login', methods=['POST'])
def login():
    print_and_log('/login', request.headers)

    if not all(key in request.json for key in ('email', 'password')):
        return Response(json.dumps({"login_status": 422, "message" : "Wrong request"}),  mimetype='application/json')
    
    if any(value == "" for value in request.json.values()):
        return Response(json.dumps({"register_status": 422, "message" : "Wrong values"}), mimetype='application/json')

    mail = request.json['email']
    cached_users = redis_client.get('users')
    if not cached_users:
        print('Populating the cache of users')
        populate_users_cache()
    
    cached_users = json.loads(redis_client.get('users'))
    found_user = None
    for user in cached_users:
        if user['email'] == mail:
            found_user = user
            break
    
    if found_user is not None and check_password_hash(found_user['password'], request.json['password']):
        access_token = create_access_token(identity = mail)
        user_id = found_user['id']
        user_session = sessions.find_one({"user_id": user_id})
        if user_session is None:
            sessions.insert_one({'user_id' : user_id, 'active_sessions' : [access_token], 'card_products': [], 'last_login': datetime.now()})
        else:
            sessions.update_one({'user_id' : user_id}, {'$push': {'active_sessions': access_token}, '$set': {'last_login': datetime.now()}})

        return Response(json.dumps({"login_status": 200, "access_token": access_token, "user_name": found_user['name'], "message": "Logged in Successfully"}), mimetype='application/json')
    
    return Response(json.dumps({"login_status": 401, "message": "Wrong E-Mail or password"}), mimetype='application/json')

@app.route('/user/logout', methods=["POST"])
@jwt_required()
def logout():
    print_and_log('/logout', request.headers)
    
    _, _, token = request.headers['Authorization'].partition(' ')
    user_mail = get_jwt_identity()
    cached_users = redis_client.get('users')
    if not cached_users:
        print('Populating the cache of users')
        populate_users_cache()
    
    cached_users = json.loads(redis_client.get('users'))
    user_id = None
    for user in cached_users:
        if user['email'] == user_mail:
            user_id = user['id']
            break
    
    if user_id is None:
        return Response(json.dumps({"status": 401, "message": "User not logged in"}),  mimetype='application/json')
    
    count = sessions.count_documents({'user_id' : user_id})
    if count == 0:
        return Response(json.dumps({"logout_status": 422, "message": "You are not logged in!"}), mimetype='application/json')
    
    sessions.update_one({'user_id' : user_id}, {'$pull': {'active_sessions': token}})

    response = jsonify({"logout_status": 200, "message": "Logged out successfully"})
    unset_jwt_cookies(response)
    
    return response

@app.route('/user/register', methods = ['POST'])
def register():
    print_and_log('/register', request.headers)
    
    if not all(key in request.json for key in ('email', 'name', 'address', 'phone_number', 'password')):
        return Response(json.dumps({"register_status": 422, "message" : "Wrong request"}),  mimetype='application/json')
    
    search_result = db.session.query(User).filter_by(email = request.json['email']).first()
    
    if search_result is not None:
        return Response(json.dumps({"register_status": 422, "message" : "E-Mail already registered"}), mimetype='application/json')
        
    if any(value == "" for value in request.json.values()):
        return Response(json.dumps({"register_status": 422, "message" : "Wrong values"}), mimetype='application/json')
    
    # Update the database
    user = User(email = request.json['email'], name = request.json['name'], address = request.json['address'], phone_number = request.json['phone_number'], password = request.json['password'])
    db.session.add(user)
    db.session.commit()
    
    cached_users = redis_client.get('users')
    if cached_users:
        cached_users_json = json.loads(cached_users)
        entry = {"id": user.id, "email": user.email, "name": user.name, "password": user.password}
        cached_users_json.append(entry)
        redis_client.set('users', json.dumps(cached_users_json))
        print('Cache updated!')
    
    return Response(json.dumps({"register_status": 200}), mimetype='application/json')

@app.route('/user/authenticate', methods=["POST"])
@jwt_required()
def authenticate():
    print_and_log('/authenticate', request.headers)
    
    user_mail = get_jwt_identity()

    cached_users = redis_client.get('users')
    if not cached_users:
        print('Populating the cache of users')
        populate_users_cache()
    
    cached_users = json.loads(redis_client.get('users'))
    user_id = None
    for user in cached_users:
        if user['email'] == user_mail:
            user_id = user['id']
            break
    
    if user_id is None:
        return Response(json.dumps({"status": 401, "message": "User not logged in"}),  mimetype='application/json')
    
    return Response(json.dumps({"status": 200, "user_id" : user_id}),  mimetype='application/json')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    args = argParser.parse_args()
    if args.id == None or args.port == None:
        print("Please specify server id and port")
        exit()
    
    server_id = args.id
    app.run(port = args.port)