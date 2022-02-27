from flask_sqlalchemy import SQLAlchemy
from models.user import User
from models.cartitem import CartItem

class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    name = db.Column(db.String, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    cartitems = db.relationship('CartItem', backref='item')

    def toDict(self):
        return{
            'id': self.id,
            'name': self.name,
            'quantity': self.quantity,
            'price':self.price
        }



#class Item(db.Model):
#    id=db.Column(db.integer,primary_key=True)
#    user_id=db.Column(db.integer,db.ForeignKey('user.id'))
#    name=db.Column(db.String,nullable=False)
#    quantity=db.Column(db.integer,nullable=False)
#    price=db.Column(db.integer,nullable=False)

#class CartItem(db.Model):
#    id = db.Column(db.Integer, primary_key=True)
#    product_id = db.Column(db.Integer, db.ForeignKey(''))


#    def toDict(self):
#        return{
#            'id': self.id,
#            'name': self.name,
#            'quantity': self.quantity,
#            'price':self.price
#        }
#-----------------------