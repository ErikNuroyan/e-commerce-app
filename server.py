from datetime import datetime
from flask import Flask, render_template, jsonify, request, Response, redirect, url_for, flash, session
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required, JWTManager, unset_jwt_cookies, verify_jwt_in_request
from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
import argparse
import json
import os

argParser = argparse.ArgumentParser()
argParser.add_argument("-id", "--id", type = int,  help="server id")
argParser.add_argument("-port", "--port", type = int,  help="port number")

server_id = None

app = Flask(__name__)
app.secret_key = "some_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///items.sqllite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

jwt = JWTManager(app)


client = MongoClient('localhost', 27017)
mongo_db = client.flask_db
products = mongo_db.products
sessions = mongo_db.sessions
orders = mongo_db.orders
responses = mongo_db.responses

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

def print_and_log(request_string):
    dt = datetime.now()
    print('Server id: ', server_id, ' Request: ', request_string, ' Date: ', dt)
    responses.insert_one({'server_id' : server_id, 'request' : request_string, 'date' : dt})
    

@app.route('/')
def home():
    print_and_log('/')
    return render_template("index.html")

@app.route('/products')
def get_products():
    product_list = list(products.find())
    all_products = []
    for product in product_list:
        if product['quantity'] > 0:
            all_products.append({"id" : str(product['_id']), "name" : product['name'], "description" : product['description'], "price" : product['price'], "quantity" : product['quantity']})
    
    print_and_log('/products')
    return Response(json.dumps(all_products),  mimetype='application/json')

@app.route('/card_products')
@jwt_required()
def get_card_products():
    _, _, token = request.headers['Authorization'].partition(' ')
    user_mail = get_jwt_identity()
    user = User.query.filter_by(email = user_mail).first()
    user_session = sessions.find_one({'user_id': user.id})

    if session is None:
        return Response(json.dumps({"status": 401, "message": "User not logged in"}),  mimetype='application/json')
    
    print_and_log('/card_products')
    return Response(json.dumps({"card_products": user_session["card_products"], "status": 200}),  mimetype='application/json')

@app.route('/add_to_card', methods=['POST'])
@jwt_required()
def add_to_card():
    _, _, token = request.headers['Authorization'].partition(' ')
    user_mail = get_jwt_identity()
    user = User.query.filter_by(email = user_mail).first()
    user_session = sessions.find_one({'user_id': user.id})

    if user_session is None:
        return Response(json.dumps({"status": 401, "message": "User not logged in"}),  mimetype='application/json')

    if 'item_id' in request.json:
        item_id = ObjectId(request.json['item_id'])
        if products.count_documents({"_id" : item_id}) == 0:
            return Response(json.dumps({"status": 422, "message": "Wrong Input"}),  mimetype='application/json')
    else:
        return Response(json.dumps({"status": 422, "message": "Wrong Input"}),  mimetype='application/json')


    sessions.update_one({'user_id': user.id}, {"$push": { "card_products": request.json['item_id']} })
    print_and_log('/add_to_card')
    
    return Response(json.dumps({"status": 200, "message": "Added to the card"}),  mimetype='application/json')

@app.route('/remove_from_card', methods=['POST'])
@jwt_required()
def remove_from_card():
    _, _, token = request.headers['Authorization'].partition(' ')
    user_mail = get_jwt_identity()
    user = User.query.filter_by(email = user_mail).first()
    user_session = sessions.find_one({'user_id': user.id})

    if user_session is None:
        return Response(json.dumps({"status": 401, "message": "Session expired"}),  mimetype='application/json')

    if 'item_id' in request.json:
        item_id = ObjectId(request.json['item_id'])
        if products.count_documents({"_id" : item_id}) == 0:
            return Response(json.dumps({"status": 422, "message": "Wrong Input"}),  mimetype='application/json')
    else:
        return Response(json.dumps({"status": 422, "message": "Wrong Input"}),  mimetype='application/json')

    sessions.update_one({'user_id': user.id}, {"$pull": { "card_products": request.json['item_id']} })
    
    print_and_log('/remove_from_card')
    return Response(json.dumps({"status": 200, "message": "Removed from the card"}),  mimetype='application/json')

@app.route('/products/add', methods=['POST'])
def add_unique_product():
    status = 200
    if 'name' in request.json:
        prod_name = request.json['name']
        count = products.count_documents({"name" : prod_name})

        if count != 0 or type(prod_name) != str or prod_name == '':
            status = 422
    else:
        status = 422
    
    if 'description' in request.json:
        prod_description = request.json['description']
        if type(prod_description) != str or prod_description == '':
            status = 422
    else:
        status = 422
    
    if 'price' in request.json:
        prod_price = request.json['price']
        if type(prod_price) != int or prod_price < 1:
            status = 422
    else:
        status = 422
    
    if 'quantity' in request.json:
        prod_quantity = request.json['quantity']
        if type(prod_quantity) != int or prod_quantity < 1:
            status = 422
    else:
        status = 422
    
    if status == 200:
        products.insert_one({'name' : prod_name, 'description' : prod_description, 'price' : prod_price, 'quantity' : prod_quantity})
        print("Product Added! name: " + prod_name + ", description: " + str(prod_description) + ", price: " + str(prod_price) + ", quantity: " + str(prod_quantity))
    
    print_and_log('/products/add')
    
    return Response(json.dumps({"add_status" : status}),  mimetype='application/json')

@app.route('/products/purchase', methods=['POST'])
@jwt_required()
def purchase():
    status = 200
    if 'item_ids' in request.json:
        item_ids = request.json['item_ids']
        for id in item_ids:
            prod_id = ObjectId(id)
            count = products.count_documents({"_id" : prod_id})
            if count == 0 or type(id) != str:
                status = 422
                break
    else:
        return Response(json.dumps({"purchase_status": 422, "message": "Unprocessable request"}),  mimetype='application/json')
    
    if status == 200:
        #TODO: Add payment verification mechanism

        prod_list = list(products.find({"_id" : {"$in" : [ObjectId(x) for x in item_ids]}}))

        prod_ids = []
        for prod in prod_list:
            if prod['quantity'] <= 0:
                return Response(json.dumps({"purchase_status": 422, "message": "Not enough products left"}),  mimetype='application/json')
            prod_ids.append(prod['_id'])
        
        user_mail = get_jwt_identity()
        user = User.query.filter_by(email = user_mail).first()
        if user is None:
            return Response(json.dumps({"purchase_status": 422, "message": "No user found"}),  mimetype='application/json')

        for prod in prod_list:
            products.update_one({"_id" : prod['_id']}, {"$set": {"quantity": prod['quantity'] - 1}})
            print("Purchased item_id: " + str(prod['_id']))
        
        orders.insert_one({'user_id' : user.id, 'products' : prod_ids, 'date' : datetime.now(), 'status' : "pending"})

    print_and_log('/products/purchase')
    
    return Response(json.dumps({"purchase_status": status, "message": "Products purchased successfully"}),  mimetype='application/json')


@app.route('/login', methods=['POST'])
def login():
    if not all(key in request.json for key in ('email', 'password')):
        return Response(json.dumps({"login_status": 422, "message" : "Wrong request"}),  mimetype='application/json')
    
    if any(value == "" for value in request.json.values()):
        return Response(json.dumps({"register_status": 422, "message" : "Wrong values"}), mimetype='application/json')

    mail = request.json['email']
    user = User.query.filter_by(email = mail).first()
    if user is not None and user.check_password(request.json['password']):
        #TODO: Make expiring tokens
        access_token = create_access_token(identity = mail)

        #TODO: Add more fields to this
        user_session = sessions.find_one({"user_id": user.id})
        if user_session is None:
            sessions.insert_one({'user_id' : user.id, 'active_sessions' : [access_token], 'card_products': [], 'last_login': datetime.now()})
        else:
            sessions.update_one({'user_id' : user.id}, {'$push': {'active_sessions': access_token}, '$set': {'last_login': datetime.now()}})

        return Response(json.dumps({"login_status": 200, "access_token": access_token, "user_name": user.name, "message": "Logged in Successfully"}), mimetype='application/json')
        
    print_and_log('/login')
    
    return Response(json.dumps({"login_status": 401, "message": "Wrong E-Mail or password"}), mimetype='application/json')

@app.route('/logout', methods=["POST"])
@jwt_required()
def logout():
    _, _, token = request.headers['Authorization'].partition(' ')
    user_mail = get_jwt_identity()
    user = User.query.filter_by(email = user_mail).first()

    count = sessions.count_documents({'user_id' : user.id})
    if count == 0:
        return Response(json.dumps({"logout_status": 422, "message": "You are not logged in!"}), mimetype='application/json')
    
    sessions.update_one({'user_id' : user.id}, {'$pull': {'active_sessions': token}})

    response = jsonify({"logout_status": 200, "message": "Logged out successfully"})
    unset_jwt_cookies(response)
    
    print_and_log('/logout')
    
    return response

@app.route('/register', methods = ['POST'])
def register():
    if not all(key in request.json for key in ('email', 'name', 'address', 'phone_number', 'password')):
        return Response(json.dumps({"register_status": 422, "message" : "Wrong request"}),  mimetype='application/json')
    
    search_result = db.session.query(User).filter_by(email = request.json['email']).first()
    
    if search_result is not None:
        return Response(json.dumps({"register_status": 422, "message" : "E-Mail already registered"}), mimetype='application/json')
        
    if any(value == "" for value in request.json.values()):
        return Response(json.dumps({"register_status": 422, "message" : "Wrong values"}), mimetype='application/json')
    
    user = User(email = request.json['email'], name = request.json['name'], address = request.json['address'], phone_number = request.json['phone_number'], password = request.json['password'])
    db.session.add(user)
    db.session.commit()
    
    print_and_log('/register')
    
    return Response(json.dumps({"register_status": 200}), mimetype='application/json')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    args = argParser.parse_args()
    if args.id == None or args.port == None:
        print("Please specify server id and port")
        exit()
    
    server_id = args.id
    app.run(port = args.port)

