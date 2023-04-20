from datetime import datetime
from flask import Flask, render_template, request, Response
from flask_jwt_extended import jwt_required, JWTManager
from redis import Redis
from pymongo import MongoClient
from bson import ObjectId
import argparse
import json
import requests

argParser = argparse.ArgumentParser()
argParser.add_argument("-id", "--id", type = int,  help="server id")
argParser.add_argument("-port", "--port", type = int,  help="port number")

server_id = None

app = Flask(__name__)
app.secret_key = "some_key"

redis_client = Redis(host='localhost', port=6379, db=0)

jwt = JWTManager(app)

client = MongoClient('localhost', 27017)
mongo_db = client.flask_db
products = mongo_db.products

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

@app.route('/')
def home():
    print_and_log('/', request.headers)
        
    return render_template("index.html")

@app.route('/products')
def get_products():
    print_and_log('/products', request.headers)
    
    cached_prods = redis_client.get('products')
    if cached_prods:
        print('Sending products from the cache')
        return Response(json.dumps(json.loads(cached_prods)), mimetype='application/json')
    
    product_list = list(products.find())
    all_products = []
    for product in product_list:
        if product['quantity'] > 0:
            all_products.append({"id" : str(product['_id']), "name" : product['name'], "description" : product['description'], "price" : product['price'], "quantity" : product['quantity']})
    
    prods_json = json.dumps(all_products)
    redis_client.set('products', prods_json, ex=60)
    
    return Response(prods_json, mimetype='application/json')

@app.route('/products/add', methods=['POST'])
def add_unique_product():
    print_and_log('/products/add', request.headers)
    
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
        # Update the DB
        entry = {'name' : prod_name, 'description' : prod_description, 'price' : prod_price, 'quantity' : prod_quantity}
        products.insert_one(entry)
        print("Product Added! name: " + prod_name + ", description: " + str(prod_description) + ", price: " + str(prod_price) + ", quantity: " + str(prod_quantity))
        
        # Update the cache if exists
        cached_prods = redis_client.get('products')
        if cached_prods:
            entry['id'] = str(entry['_id'])
            entry.pop('_id', None)
            cached_prods_json = json.loads(cached_prods)
            cached_prods_json.append(entry)
            redis_client.set('products', json.dumps(cached_prods_json))
            print('Cache updated!')
    
    return Response(json.dumps({"add_status" : status}),  mimetype='application/json')

@app.route('/products/purchase', methods=['POST'])
@jwt_required()
def purchase():
    print_and_log('/products/purchase', request.headers)
    
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
        prod_list = list(products.find({"_id" : {"$in" : [ObjectId(x) for x in item_ids]}}))

        prod_ids = []
        for prod in prod_list:
            if prod['quantity'] <= 0:
                return Response(json.dumps({"purchase_status": 422, "message": "Not enough products left"}),  mimetype='application/json')
            prod_ids.append(str(prod['_id']))
        
        # Send a request to user service to authenticate
        url = 'http://127.0.0.1:5003/user/authenticate'
        headers = {k:v for k,v in request.headers}
        response = requests.post(url = url, headers=headers).json()
        
        if response['status'] != 200:
            return Response(json.dumps(response),  mimetype='application/json')

        user_id = response['user_id']
        # Update the database
        for prod in prod_list:
            products.update_one({"_id" : prod['_id']}, {"$set": {"quantity": prod['quantity'] - 1}})
            print("Purchased item_id: " + str(prod['_id']))
        
        # Update the cache if it exists
        cached_prods = redis_client.get('products')
        if cached_prods:
            def changer(item):
                item["quantity"] -= 1
                return item
            
            cached_prods_json = json.loads(cached_prods)
            updated_cache = [changer(item) if item['id'] in prod_ids else item for item in cached_prods_json]
            redis_client.set('products', json.dumps(updated_cache))
            print('Cache updated!')
        
        # Send a request to orders service to add an order
        url = 'http://127.0.0.1:5005/orders/add'
        headers = {k:v for k,v in request.headers}
        response = requests.post(url = url, json = json.dumps({"user_id" : user_id, "products" : prod_ids}), headers=headers).json()

        if response['status'] != 200:
            return Response(json.dumps({"purchase_status": response['status'], "message": "Error adding order"}),  mimetype='application/json')
    
    return Response(json.dumps({"purchase_status": status, "message": "Products purchased successfully"}),  mimetype='application/json')

@app.route('/products/validate_item')
def validate_product_item():
    print_and_log('/products/validate_item', request.headers)
    
    cached_prods = redis_client.get('products')
    if cached_prods:
        prods = json.loads(cached_prods)
        for prod in prods:
            if prod["id"] == request.json['item_id']:
                return Response(json.dumps({"status": 200, "is_valid": 1}), mimetype='application/json')
    
    is_valid = products.count_documents({"_id" : ObjectId(request.json['item_id'])}) == 0
    
    return Response(json.dumps({"status": 200, "is_valid": is_valid}), mimetype='application/json')

if __name__ == "__main__":
    args = argParser.parse_args()
    if args.id == None or args.port == None:
        print("Please specify server id and port")
        exit()
    
    server_id = args.id
    app.run(port = args.port)

