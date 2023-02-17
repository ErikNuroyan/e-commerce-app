from flask import Flask, render_template, jsonify, request, Response, redirect
from flask_sqlalchemy import SQLAlchemy
import json

app = Flask(__name__)
app.secret_key = "some_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///items.sqllite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False, unique=True)
    price = db.Column(db.Integer, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    items = db.relationship('ItemTable', backref='item', lazy=True,       cascade='save-update, merge, delete',
        passive_deletes=True)
    
    def __init__(self, name, price, quantity):
        self.name = name
        self.price = price
        self.quantity = quantity
    
class ItemTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id', ondelete='CASCADE'),
        nullable=False)
    
    def __init__(self, item_id):
        self.item_id = item_id
    
@app.route('/')
def home():
    return render_template("index.html")

@app.route('/store/products')
def send_products():
    item_list = db.session.query(ItemTable, Item).join(Item, ItemTable.item_id == Item.id).all()
    all_products = []
    for item in item_list:
        all_products.append({"id" : item[0].id, "name" : item[1].name, "price": item[1].price})
        
    return Response(json.dumps(all_products),  mimetype='application/json')

@app.route('/unique_products')
def send_unique_products():
    item_list = db.session.query(Item).all()
    all_products = []
    for item in item_list:
        all_products.append({"id" : item.id, "name" : item.name, "price": item.price})
        
    return Response(json.dumps(all_products),  mimetype='application/json')


@app.route('/unique_products/add', methods=['POST'])
def add_unique_product():
    status = 200
    if 'name' in request.json:
        prod_name = request.json['name']
        search_result = db.session.query(Item).filter_by(name = prod_name).first()
        
        if search_result is not None or type(prod_name) != str or prod_name == '':
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
        new_item = Item(prod_name, prod_price, prod_quantity)
        db.session.add(new_item)
        db.session.commit()
        print("Product Added! name: " + prod_name + ", price: " + str(prod_price) + ", quantity: " + str(prod_quantity))
    
    return Response(json.dumps({"add_status" : status}),  mimetype='application/json')

@app.route('/store/add', methods=['POST'])
def add_to_store():
    status = 200
    if 'selected_item_id' in request.json:
        item_id = request.json['selected_item_id']
        search_result = db.session.query(Item).filter_by(id = item_id).first()
        
        if search_result is None:
            status = 422
    else:
        status = 422

    if status == 200:
        store_item_count = db.session.query(ItemTable).filter_by(item_id = item_id).count()
        if store_item_count < search_result.quantity:
            new_item = ItemTable(item_id)
            db.session.add(new_item)
            db.session.commit()
            print("Product id added to ItemTable: " + str(item_id))
        else:
            status = 422
    
    return Response(json.dumps({"add_to_store_status" : status}),  mimetype='application/json')

@app.route('/store/purchase', methods=['POST'])
def purchase():
    status = 200
    if 'item_id' in request.json:
        item_id = request.json['item_id']
        item = db.session.query(ItemTable).filter_by(id=item_id).first()
        if item is None or type(item_id) != int:
            status = 422
    else:
        status = 422
    
    #Handle the purchase in the later homeworks
    if status == 200:
        print("Purchased item_id: " + str(item_id))
    
    return Response(json.dumps({"purchase_status": status}),  mimetype='application/json')
    
@app.route('/store/delete', methods=['POST'])
def delete():
    status = 200
    if 'item_id' in request.json:
        item_id = request.json['item_id']
        item = db.session.query(ItemTable).filter_by(id=item_id).first()
        if item is None or type(item_id) != int:
            status = 422
    else:
        status = 422
    
    if status == 200:
        db.session.query(ItemTable).filter_by(id=item_id).delete()
        db.session.commit()
        print("Deleted item_id: " + str(item_id))
    
    return Response(json.dumps({"delete_status": status}),  mimetype='application/json')

@app.route('/store/update', methods=['PUT'])
def update():
    status = 200
    if 'replace_item_id' in request.json and 'selected_item_id' in request.json:
        replace_item_id = request.json['replace_item_id']
        selected_item_id = request.json['selected_item_id']
        replace_item = db.session.query(ItemTable).filter_by(id = replace_item_id).first()
        selected_item = db.session.query(Item).filter_by(id = selected_item_id).first()
        if replace_item is None or type(replace_item_id) != int or selected_item is None or type(selected_item_id) != int:
            print(replace_item, " ", type(replace_item_id) != int, " ", selected_item, " ", type(selected_item_id))
            status = 422
    else:
        status = 422
    
    print(status)

    if status == 200:
        old_count = db.session.query(ItemTable).filter_by(item_id = selected_item_id).count()
        if old_count < selected_item.quantity:
            replace_item.item_id = selected_item_id
            db.session.commit()
            print("Updated item_id: " + str(replace_item_id))
        else:
            status = 422
    
    return Response(json.dumps({"update_status": status}),  mimetype='application/json')

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    
    app.run(port = 8787)

