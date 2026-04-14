from datetime import UTC, datetime, timezone
from typing import List, Optional

from flask import Flask, jsonify, request 
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from marshmallow import ValidationError
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, Integer, String, Table
from sqlalchemy.sql import func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

#========== Initialization Flask ===========

app = Flask(__name__)

#========== Flask Configuration ===========

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:Jahvante.97.mysql@localhost/e_commerce'

#========== Create Base Class ===========


class Base(DeclarativeBase):
    pass

#========== Extensions Initialization ===========

db = SQLAlchemy(app, model_class=Base)
ma = Marshmallow(app)

db.init_app(app)
ma.init_app(app)

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

    user_orders : Mapped[List["Order"]] = relationship(back_populates="users")




class Order(Base):
    __tablename__ = "orders"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    
    users: Mapped["User"] = relationship( back_populates="user_orders")
    products: Mapped[List["Product"]] = relationship(secondary=order_product, back_populates="orders")


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    product_name: Mapped[str] = mapped_column(String(100), nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)

    orders: Mapped[List["Order"]] = relationship(secondary=order_product, back_populates="products")
    


#========== Schemas ===========

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True

class ProductSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Product

class OrderSchema(ma.SQLAlchemyAutoSchema):
    products = ma.Nested(ProductSchema, many=True)
    class Meta:
        model = Order
        include_fk = True
        dump_only = ("id", "order_date")

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
    
    new_user = user_data
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
        user_data = request.get_json() or {}
    except ValidationError as err:
        return jsonify(err.messages), 400

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.name = user_data.get("name", user.name)
    user.email = user_data.get("email", user.email)
    user.address = user_data.get("address", user.address)

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
     

    return products_schema.jsonify(product_data), 201

#========== Update ===========

@app.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    try:
        product_data = request.get_json() or {}
    except ValidationError as err:
        return jsonify(err.messages), 400

    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    product.product_name = product_data.get("product_name", product.product_name)
    product.price = product_data.get("price", product.price)

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
    
    new_order = Order(user_id=order_data["user_id"])
    db.session.add(new_order)
    db.session.commit()

    return order_schema.jsonify(new_order), 201

#========== Read ===========

@app.route("/orders/users/<int:user_id>", methods=["GET"])
def get_orders_per_user(user_id):
    try:
        user = db.session.get(User, user_id)
    except ValidationError as err:
        return jsonify(err.messages), 400

    if not user:
        return jsonify({"error": "User not found"}), 404

    return orders_schema.jsonify(user.user_orders), 200


@app.route("/orders/<int:order_id>/products", methods=["GET"])
def get_products_in_order(order_id):
    try:
        order_data = db.session.get(Order, order_id)
        
    except ValidationError as err:
        return jsonify(err.messages), 400
     

    return order_schema.jsonify(order_data), 201

#========== Update ===========

@app.route("/orders/<int:order_id>/add_product/<int:product_id>", methods=["PUT"])
def add_product_to_order(order_id, product_id):
    try:
        order = db.session.get(Order, order_id)
    except ValidationError as err:
        return jsonify(err.messages), 400

    if not order:
        return jsonify({"error": "Order not found"}), 404

    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    order.products.append(product)

    db.session.commit()
    return order_schema.jsonify(order), 200

#========== Delete ===========

@app.route("/orders/<int:order_id>/remove_product/<int:product_id>", methods=["DELETE"])
def remove_product_from_order(order_id, product_id):
    try:
        order = db.session.get(Order, order_id)
    except ValidationError as err:
        return jsonify(err.messages), 400

    if not order:
        return jsonify({"error": "Order not found"}), 404

    product = db.session.get(Product, product_id)
    if not product:
        return jsonify({"error": "Product not found"}), 404

    if product in order.products:
        order.products.remove(product)

    db.session.commit()
        
    db.session.delete(order)
    db.session.commit()
    return order_schema.jsonify(order), 200

#========== Run App ===========

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        # db.drop_all()
        
    app.run(debug=True)