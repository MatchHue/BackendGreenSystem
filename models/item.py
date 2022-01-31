from flask_sqlalchemy import SQLAlchemy
from models.user import User

class Item(db.Model):
    id=db.Column(db.integer,primary_key=True)
    user_id=db.Column(db.integer,db.ForeignKey('user.id'))
    name=db.Column(db.String,nullable=False)
    quantity=db.Column(db.integer,nullable=False)
    price=db.Column(db.integer,nullable=False)


    def toDict(self):
        return{
            'id': self.id,
            'name': self.name,
            'quantity': self.quantity,
            'price':self.price
        }