from flask import Flask, render_template, jsonify, request, Response
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
    items = db.relationship('ItemTable', backref='item', lazy=True)

class ItemTable(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'),
        nullable=False)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/products')
def send_products():
    item_list = db.session.query(ItemTable, Item).join(Item, ItemTable.item_id == Item.id).all()
    print(item_list)
    all_products = []
    for item in item_list:
        all_products.append({"id" : str(item[0].id), "name" : item[1].name, "price": item[1].price})
        
    return Response(json.dumps(all_products),  mimetype='application/json')

@app.route('/purchase', methods=['POST'])
def purchase():
    id = request.json['item_id']
    print("Purchased item_id: " + str(id))
    return 'OK'
    

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    
    app.run(port = 8787)

