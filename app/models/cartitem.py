from flask_sqlalchemy import SQLAlchemy
from models.item import Item


class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('id'))