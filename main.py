from flask import Flask, render_template,request,redirect,url_for,redirect,jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///test.db'
db=SQLAlchemy(app)




#Models

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
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
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    name=db.Column(db.String,nullable=False)
    image=db.Column(db.String,nullable=False)
    quantity=db.Column(db.Integer,nullable=False)
    price=db.Column(db.Integer,nullable=False)
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
    id=db.Column(db.Integer,primary_key=True)
    item_id=db.Column(db.Integer,db.ForeignKey('item.id'))



@app.route('/',methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/test',methods=['GET'])
def testroute():
    return "<p1>TEST<p1>"


@app.route('/signup',methods=['POST'])
def signup():
    return jsonify(message="User Created"),200

@app.route('/login',methods=['POST'])
def login():
    return jsonify(message="Login Successful"),200

@app.route('/get_all_users',methods=['GET'])
def get_all_users():

    users=[{
        "id":1,
        "email": "marc123@mail.com",
        "username":"Marc"
    },
    {
        "id":2,
        "email": "matthew234@mail.com",
        "username":"Matthew"   
    },
    {
        "id":3,
        "email":"michael567@mail.com",
        "username":"Michael"
    }]
    return jsonify(users)




if __name__=="__main__":
    app.run(debug=True)