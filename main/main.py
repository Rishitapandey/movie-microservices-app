from flask import Flask
from flask import Flask, jsonify, abort
from flask_cors import CORS
from sqlalchemy import UniqueConstraint
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dataclasses import dataclass
from producer import publish
import requests
app=Flask(__name__)
CORS(app, resources={
    r"/api/*": {
        "origins": ["http://localhost:3000"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})
app.config["SQLALCHEMY_DATABASE_URI"] = 'mysql://root:root@db/main'
CORS(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

@dataclass
class Product(db.Model):
    id: int
    title: str
    image: str

    id = db.Column(db.Integer, primary_key=True, autoincrement=False)
    title = db.Column(db.String(200))
    image = db.Column(db.String(200))

@dataclass
class ProductUser(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    product_id = db.Column(db.Integer)

    UniqueConstraint('user_id', 'product_id', name='user_product_unique')

@app.route('/api/products')
def index():
    return jsonify(Product.query.all())


@app.route('/api/products/<int:id>/like', methods=['POST'])
def like(id):
    req = requests.get('http://docker.for.mac.localhost:8000/api/user')
    if req.status_code != 200:
       abort(400, 'Unable to fetch user data')

    try:
      json = req.json()
    except ValueError:
      abort(400, 'Invalid user response format')

    try:
        productUser = ProductUser(user_id=json['id'], product_id=id)
        db.session.add(productUser)
        db.session.commit()

        publish('product_liked',id)
    except:
        abort(400, 'You already liked this product')

    product = Product.query.get(id)
    if not product:
        abort(404, 'Product not found')

    return jsonify({
        'id': product.id,
        'image': product.image,
        'message': 'success'
    })
@app.route('/api/products/<int:id>/dislike', methods=['POST'])
def dislike(id):
    req = requests.get('http://docker.for.mac.localhost:8000/api/user')
    if req.status_code != 200:
        abort(400, 'Unable to fetch user data')

    try:
        json = req.json()
    except ValueError:
        abort(400, 'Invalid user response format')

    product_user = ProductUser.query.filter_by(user_id=json['id'], product_id=id).first()
    if not product_user:
        abort(400, 'You have not liked this product yet')

    db.session.delete(product_user)
    db.session.commit()
    publish('product_disliked', id)

    return jsonify({'message': 'dislike removed', 'product_id': id})
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
