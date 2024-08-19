from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user
import secrets

app = Flask(__name__)
app.config['SECRET_KEY'] = secrets.token_hex()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'

login_manager = LoginManager()
db = SQLAlchemy(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
CORS(app)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=True)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route('/login', methods=["POST"])
def login():
        data = request.json
        #@user = db.session.query(User).filter_by(username=data.get("username")).first()
        user = User.query.filter_by(username=data.get("username")).first()
        
        if user and data.get("password") == user.password:
            login_user(user)
            return jsonify({"message": "Logged in successfully!"})
        return jsonify({"message":"Unauthorized. Invalid Credentials"}), 401

@app.route('/logout', methods=["POST"])
@login_required
def logout():
    logout_user()
    return jsonify({"message":"Logout successfully!"})

@app.route('/api/products/add', methods=["POST"])
@login_required
def add_product():
    data = request.json
    if 'name' in data and 'price' in data:
        product = Product(name=data["name"],price=data["price"],description=data.get("description", ""))
        db.session.add(product)
        db.session.commit()
        return jsonify({"message":"Product added succesfully!"}), 201
    return jsonify({"message":"Invalid product data"}), 400

@app.route('/api/products/delete/<int:product_id>', methods=["DELETE"])
def delete_product(product_id):
    product = db.session.get(Product, product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message":"Product deleted succesfully!"})
    return jsonify({"message":"Product not found"}), 404

@app.route('/api/products/<int:product_id>',methods=["GET"])
def get_products_details(product_id):
    product = db.session.get(Product, product_id)
    if product:
        return jsonify({
            "id":product.id,
            "name":product.name,
            "price":product.price,
            "description":product.description
        })
    return jsonify({"message":"Product not found"}), 404

@app.route('/api/products/update/<int:product_id>',methods=["PUT"])
@login_required
def update_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"message":"Product not found"}), 404
    
    data = request.json
    if 'name' in data: 
        product.name = data['name']
    if 'price' in data:
        product.price = data['price']
    if 'description' in data:
        product.description = data['description']

    db.session.commit()
    return jsonify({"message":"Product update succesfully!"})

@app.route('/api/products/', methods=['GET'])
def get_all_products():
    products = db.session.query(Product).all()
    product_list = []
    for product in products:
        product_data = {
            "id":product.id,
            "name":product.name,
            "price":product.price,
            "description":product.description
        }

        product_list.append(product_data)
    return jsonify(product_list)

@app.route('/')
def home():
    return f'Hello Word'

if __name__ == "__main__":
    app.run(debug=True)