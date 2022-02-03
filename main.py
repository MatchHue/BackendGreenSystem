from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app=Flask(__name__)




#Models

class User(db.Model):
    id=db.Column(db.integer,primary_key=True)
    username=db.Column(db.String,unique=True,nullable=False)
    password=db.Column(db.String,nullable=False)
    items=db.relationship('Item',backref='user')


    def toDict(self):
        return{
            'id': self.id,
            'username': self.username,
            'password': self.password
        }

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password, method='sha256')
    
    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)
    
    def __repr__(self):
        return '<User {}>'.format(self.username)



class Item(db.Model):
    id=db.Column(db.integer,primary_key=True)
    user_id=db.Column(db.integer,db.ForeignKey('user.id'))
    name=db.Column(db.String,nullable=False)
    image=db.COlumn(db.String,nullable=False)
    quantity=db.Column(db.integer,nullable=False)
    price=db.Column(db.integer,nullable=False)
    cart_items=db.relationship('Item',backref='item')


    def toDict(self):
        return{
            'id': self.id,
            'name': self.name,
            'image':self.image,
            'quantity': self.quantity,
            'price':self.price
        }

class Cart(db.Model):
    id=db.Column(db.integer,primary_key=True)
    item_id=db.Column(db.integer,db.ForeignKey('item.id'))



if __name__=="__main__":
    app.run(debug=True)