from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import json
from flask_cors import CORS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///shop.sqlite3'
app.config['SECRET_KEY'] = "random string"
CORS(app=app)
db = SQLAlchemy(app)

# Models
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    def __repr__(self):
        return f'<Client {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name
        }


class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product = db.Column(db.String(50))
    price = db.Column(db.Float())
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'))
    client = db.relationship('Client', backref=db.backref('orders', lazy=True)) #i combined relationship

    def __repr__(self):
        return f'<Order {self.product}>'

# Routes
@app.route("/clients", methods=['GET'])
def get_clients():
    clients = Client.query.all()
    client_dicts = [{'id': client.id, 'name': client.name} for client in clients]
    json_data = json.dumps(client_dicts)
    return json_data



@app.route('/new_client', methods=['POST'])
def new_client():
    data = request.get_json()
    name = data.get('name')
    client = Client(name=name)
    db.session.add(client)
    db.session.commit()
    return jsonify({'message': 'New client created.'})


#http://127.0.0.1:5000/all_clients

@app.route('/all_clients', methods=['GET'])
def all_clients():
    clients = Client.query.all()
    return jsonify({'data': [{
        'id': client.id,
        'name': client.name,
        'orders': [o.product for o in client.orders]
    } for client in clients]})


@app.route('/new_order', methods=['POST'])
def new_order():
    data = request.get_json()
    product = data.get('product')
    price = data.get('price')
    client_id = data.get('client_id')
    order = Order(product=product, price=price, client_id=client_id)
    db.session.add(order)
    db.session.commit()
    return jsonify({'message': 'New order created.'})


#http://127.0.0.1:5000/all_orders

@app.route('/all_orders', methods=['GET'])
def all_orders():
    orders = Order.query.all()
    return jsonify({'data': [{
        'id': order.id,
        'product': order.product,
        'price': order.price,
        'client_id': order.client_id
    } for order in orders]})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)