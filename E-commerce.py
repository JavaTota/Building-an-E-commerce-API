from datetime import datetime
from typing import List, Optional

from flask import Flask, jsonify, request 
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError
from sqlalchemy import Column, DateTime, ForeignKey, Integer, Integer, String, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

#========== Initialization Flask ===========

app = Flask(__name__)

#========== Flask Configuration ===========

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Jahvante.97.mysql@localhost/e_commerce'

#========== Create Base Class ===========


class Base(DeclarativeBase):
    pass

#========== Initialization  ===========

db = SQLAlchemy(app, model_class=Base)
ma = Marshmallow(app)

#========== Association Table  ===========

order_product = Table(
    "order_product",
    Base.metadata,
    Column("order_id", ForeignKey("orders.id"), primary_key=True),
    Column("product_id", ForeignKey("products.id"), primary_key=True)
)

#========== Models ===========

class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(String(200))
    email: Mapped[Optional[str]] = mapped_column(String(200), unique=True)



class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_date: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now)
   
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))

class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_name: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(String(50), nullable=False)
    


#========== Schemas ===========

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User

class OrderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Order
        include_fk = True

class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product

user_schema = UserSchema()
users_schema = UserSchema(many=True) # to serialize a list of users
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True) # to serialize a list of orders
product_schema = ProductSchema()
products_schema = ProductSchema(many=True) # to serialize a list of products

#==================== User Routes =====================


#========== Create ===========


@app.route("/users", methods=["POST"])
def create_user():
    try:
        user_data = user_schema.load(request.json)
        
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_user = User(name=user_data["name"], email=user_data["email"])
    db.session.add(new_user)
    db.session.commit()

    return user_schema.jsonify(new_user), 201


#========== Read ===========


@app.route("/users/<int:user_id>", methods=["GET"])
def get_user(user_id):
    try:
        user_data = db.session.get(User, user_id)
        
    except ValidationError as err:
        return jsonify(err.messages), 400
     

    return user_schema.jsonify(user_data), 201


@app.route("/users", methods=["GET"])
def get_users():
    try:
        users_data = db.session.query(User).all()
        
    except ValidationError as err:
        return jsonify(err.messages), 400
     

    return users_schema.jsonify(users_data), 201


#========== Update ===========


@app.route("/users/<int:user_id>", methods=["PUT"])
def update_user(user_id):
    try:
        user_data = user_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    for key, value in user_data.items():
        setattr(user, key, value)

    db.session.commit()
    return user_schema.jsonify(user), 200


#========== Delete ===========


@app.route("/users/<int:user_id>", methods=["DELETE"])
def delete_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted"}), 200


#==================== Product Routes =====================

#========== Create ===========

@app.route("/products", methods=["POST"])
def create_product():
    try:
        product_data = product_schema.load(request.json)
        
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_product = Product(product_name=product_data["product_name"], price=product_data["price"])
    db.session.add(new_product)
    db.session.commit()

    return product_schema.jsonify(new_product), 201

#========== Read ===========

@app.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    try:
        product_data = db.session.get(Product, product_id)
        
    except ValidationError as err:
        return jsonify(err.messages), 400
     

    return product_schema.jsonify(product_data), 201

@app.route("/products", methods=["GET"])
def get_products():
    try:
        product_data = db.session.query(Product).all()
        
    except ValidationError as err:
        return jsonify(err.messages), 400
     

    return product_schema.jsonify(product_data), 201

#========== Update ===========

@app.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    for key, value in product_data.items():
        setattr(product, key, value)

    db.session.commit()
    return product_schema.jsonify(product), 200

#========== Delete ===========

@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted"}), 200


#==================== Order Routes =====================


#========== Create ===========

@app.route("/orders", methods=["POST"])
def create_order():
    try:
        order_data = order_schema.load(request.json)
        
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    new_order = Order(order_items=order_data["order_items"], total_price=order_data["total_price"])
    db.session.add(new_order)
    db.session.commit()

    return order_schema.jsonify(new_order), 201

#========== Read ===========

@app.route("/orders/user/<int:user_id>", methods=["GET"])
def get_order(user_id):
    try:
        order_data = db.session.get(Order, user_id)
        
    except ValidationError as err:
        return jsonify(err.messages), 400
     

    return order_schema.jsonify(order_data), 201


@app.route("/orders/<order_id>/products", methods=["GET"])
def get_order_products(order_id):
    try:
        order_data = db.session.get(Order, order_id)
        
    except ValidationError as err:
        return jsonify(err.messages), 400
     

    return order_schema.jsonify(order_data), 201

#========== Update ===========

@app.route("/orders/<order_id>/add_product/<product_id>", methods=["PUT"])
def update_order(order_id):
    try:
        order_data = order_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    for key, value in order_data.items():
        setattr(order, key, value)

    db.session.commit()
    return order_schema.jsonify(order), 200

#========== Delete ===========

@app.route("/orders/<order_id>/remove_product/<product_id>", methods=["DELETE"])
def delete_order(order_id):
    order = db.session.get(Order, order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    db.session.delete(order)
    db.session.commit()
    return jsonify({"message": "Order deleted"}), 200


#========== Run App ===========

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # db.drop_all()
        
    app.run(debug=True)