from ctypes import sizeof
import json
from unicodedata import numeric
from flask import Flask, render_template,request,redirect, session,url_for,redirect,jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
import idna
from sqlalchemy import Numeric
from wtforms import StringField,SubmitField, PasswordField, BooleanField, ValidationError,EmailField, DecimalField, SelectField,IntegerField,FloatField
from wtforms.validators import DataRequired, EqualTo, Length
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, login_manager, login_required, logout_user, current_user, LoginManager
import os
import requests
import folium
import string,random


app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///test.db'
app.config['SECRET_KEY']='CharizardIsTheBestStarter'

db=SQLAlchemy(app)




#Login Setup
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

locationdata='http://ip-api.com/json/'


class LoginForm(FlaskForm):
    email=EmailField("Email",validators=[DataRequired()])
    password=PasswordField("Password",validators=[DataRequired()])
    submit=SubmitField("Login")

class SignUpForm(FlaskForm):
    username=StringField("Username",validators=[DataRequired()])
    image=FileField(label="image",validators=[FileAllowed(['jpg','png'])])
    email=EmailField("Email",validators=[DataRequired()])
    phone_number=StringField("Contact",validators=[DataRequired()])
    password=PasswordField("Password",validators=[DataRequired()])
    submit=SubmitField("Submit")

class ItemForm(FlaskForm):
    name=StringField("Username",validators=[DataRequired()])
    image=FileField(label="image",validators=[FileAllowed(['jpg','png'])])
    quantity=IntegerField("Quantity",validators=[DataRequired()])
    price=FloatField("Price",validators=[DataRequired()])
    delivery=SelectField("Delivery",choices=[("Deliver to Client"),("Have Client Pickup order")])
    submit=SubmitField("Add Item")
    


#Models

class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String,unique=True,nullable=False)
    pfp=db.Column(db.String,nullable=False)
    email=db.Column(db.String,unique=True,nullable=False)
    phone_number=db.Column(db.Integer,unique=True)
    password=db.Column(db.String,nullable=False)
    longtitude=db.Column(db.Numeric,nullable=False)
    latitude=db.Column(db.Numeric,nullable=False)
    items=db.relationship('Item',backref='user')
    cart=db.relationship('Cart',backref='user')


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
    price=db.Column(db.Float,nullable=False)
    delivery=db.Column(db.String,nullable=False)
    #cart_items=db.relationship('Cart',backref='item')


    def toDict(self):
        return{
            'id': self.id,
            'name': self.name,
            'image':self.image,
            'quantity': self.quantity,
            'price':self.price
        }

class Cart(db.Model):
    cart_id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    item_id=db.Column(db.Integer,nullable=False)  
    cart_quantity=db.Column(db.Integer,nullable=False)

class Order(db.Model):
    order_id=db.Column(db.Integer,primary_key=True)
    seller_id=db.Column(db.Integer,nullable=False)
    buyer_id=db.Column(db.Integer,nullable=False)
    item_bought=db.Column(db.Integer,nullable=False)
    quantity_bought=db.Column(db.Integer,nullable=False)
    order_code=db.Column(db.String,nullable=False)

def getlocation():
    response=requests.get("http://ip-api.com/json/")
    data=response.json()
    return data

@app.route('/',methods=['GET'])
def index():
    users=User.query.all()
    items=Item.query.all()
    images=[]
    for item in items:
        images.append(url_for('static',filename='item_images/+item.image'))
    return render_template('index.html',users=users,items=items,images=images)

@app.route('/get_location_data',methods=['GET'])
def testroute():
    response=requests.get("http://ip-api.com/json/")
    data=response.json()
    return data


def savepfp(picture_file):
    picture=picture_file.filename
    picture_path=os.path.join(app.root_path,'static/pfp',picture)
    picture_file.save(picture_path)
    return picture

@app.route('/signup',methods=['GET','POST'])
def signup():
    location=getlocation()
    form=SignUpForm()
    lat=float(location['lat'])
    lon=float(location['lon'])
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user is None:
            profile_image=savepfp(form.image.data)
            newUser=User(username=form.username.data,pfp=profile_image,email=form.email.data,password=form.password.data,
            phone_number=form.phone_number.data,
            longtitude=lon,latitude=lat)
            newUser.set_password(newUser.password)
            db.session.add(newUser)
            db.session.commit()
        form.username.data=''
        form.email.data=''
        return redirect(url_for('index'))
    return render_template('signup.html',form=form,lat=lat,lon=lon)

@app.route('/login',methods=['POST','GET'])
def login():
    form=LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                flash("Logged In Successful")
                return redirect(url_for('index'))
            else:
                flash("Incorrect Password")
    return render_template('login.html',form=form)


@app.route('/logout',methods=['GET','POST'])
@login_required
def logout():
    logout_user()
    flash("Succesfully Logged Out")
    return redirect(url_for('login')) 

@app.route('/get_all_users',methods=['GET'])
def get_all_users():

    users=User.query.all()
    return users


@app.route('/get_all_sellers',methods=['GET'])
def get_all_sellers():

    sellers=User.query.all()
    return render_template('sellers.html',sellers=sellers)


@app.route('/get_user_items/<int:id>',methods=['GET'])
def get_user_items(id):
    user=User.query.get(id)
    items=user.items
    return render_template('user_items.html',user=user,items=items)


def saveimage(picture_file):
    picture=picture_file.filename
    picture_path=os.path.join(app.root_path,'static/item_images',picture)
    picture_file.save(picture_path)
    return picture

@app.route('/list_items',methods=['GET','POST'])
@login_required
def list_items():
    form=ItemForm()
    if form.validate_on_submit():
        lister=current_user.id
        image_file=saveimage(form.image.data)
        print(image_file)
        newItem=Item(name=form.name.data,image=image_file,quantity=form.quantity.data,price=form.price.data,
        delivery=form.delivery.data,user_id=lister)
        db.session.add(newItem)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('listitem.html',form=form)

@app.route('/item_details/<int:id>',methods=['GET'])
def item_details(id):
    item=Item.query.get(id)
    return render_template('item_details.html',item=item)


@app.route('/rate_user',methods=['POST'])
#@login_required
def rate_user():
    rated={
        "user_id":2,
        "rating":3
    }
    return jsonify(message='User rated'),rated

@app.route('/get_rating',methods=['GET'])
def get_rating():
    user_rating={
    "rating":3
    }
    return user_rating

@app.route('/get_all_items',methods=['GET'])
def get_all_items():
    all_items={"items":[
    {
    "user_id":2,
    "name":"pumpkin",
    "price":"6$ per pound",
    "image":"pumpkin.png",
    "quantity":"40lbs"
    },
    {
    "user_id":2,
    "name":"mango",
    "price":"$3 per",
    "image":"mango.png",
    "quantity":20
    },
    {
    "user_id":2,
    "item_id":3,
    "name":"Pommecythere",
    "price":"$2 per",
    "image":"pommecythere.png",
    "quantity":100
    }
    ]}
    return all_items


@app.route('/bulk_purchase',methods=['GET'])
#@login_required
def bulk_purchase():
    items={
    "user": [
    {
    "user_id": 2,
    "email": "matthew234@mail.com",
    "username": "Matthew",
    "items":[
    {
    "name":"Pommecythere",
    "price":"$2 per",
    "image":"pommecythere.png",
    "quantity":50
    }
        ]
    }
         ]
    }
    return items



@app.route('/search',methods=['GET'])
def search():
    results={
            "items": [
        {
        "name":"mango",
        "price":"$3 per",
        "image":"pumpkin.png",
        "quantity":20
        }
                ]

        }
    return results

@app.route('/sort_by_price',methods=['GET'])
def sort_by_price():
    sorted={
            "items":[
            {
            "item_id":3,
            "name":"Pommecythere",
            "price":"$2 per",
            "image":"pommecythere.png",
            "quantity":100
            },
            {
            "item_id":2,
            "name":"mango",
            "price":"$3 per",
            "image":"pumpkin.png",
            "quantity":20
            },
            {
            "item_id":1,
            "name":"pumpkin",
            "price":"6$ per pound",
            "image":"pumpkin.png",
            "quantity":"40lbs"
            }
                 ]
    }
    return sorted



@app.route('/sort_by_name',methods=['GET'])
def sort_by_name():
    results={
    "items": [
        {
            "item_id": 1,
            "name": "mango",
            "price": "$3 per",
            "image": "pumpkin.png",
            "quantity": 20
        },
        {
            "item_id": 3,
            "name": "Pommecythere",
            "price": "$2 per",
            "image": "pommecythere.png",
            "quantity": 100
        },
        {
            "item_id": 1,
            "name": "pumpkin",
            "price": "6$ per pound",
            "image": "pumpkin.png",
            "quantity": "40lbs"
        }
            ]
    }
    return results


@app.route('/get_item_detail',methods=['GET'])
def get_item_detail():
    item_details={
    "item_id": 1,
    "name": "mango",
    "price": "$3 per",
    "image": "pumpkin.png",
    "quantity": 20,
    "user": {
        "username": "Matthew"
        }
    }
    return item_details

@app.route('/add_to_cart/<int:id>',methods=['POST'])
@login_required
def add_to_cart(id):
    item_id=id
    user=current_user.id
    data=request.form
    cartItem=Cart(item_id=item_id,cart_quantity=data['quantity'],user_id=user)
    db.session.add(cartItem)
    db.session.commit()
    return redirect(url_for('index'))
  


@app.route('/delivery' ,methods=['GET', 'POST'])
@login_required
def checkout():
    form=AddressForm()
    if form.validate_on_submit():
        user=User.query.get(current_user.id)
        address=form.address.data,user_id=current_user.id
        delivery=form.delivery.data,user_id=current_user.id
        db.session.add(address)
        db.session.commit()
        return redirect(url_for('cart'))
    return render_template('checkout.html',address=address,user=user)





@app.route('/get_cart',methods=['GET'])
@login_required
def get_cart():
    user=User.query.get(current_user.id)
    items=[]
    carts=Cart.query.all()
    for c in user.cart:
        item=Item.query.get(c.item_id)
        cart=Cart.query.get(c.cart_id)
        items.append(item)
        items.append(cart)
    return render_template('cart.html',items=items,user=user,carts=carts)


def  generate_order_code():
    letters = string.ascii_lowercase
    digits=string.digits
    code=''.join(random.choice(letters) for i in range(5))
    numbers=''.join(random.choice(digits) for i in range(5))
    code=code+numbers
    new_code=''.join(random.sample(code, len(code)))
    return new_code

@app.route("/test_code",methods=['GET'])
def test_code():    
    code=generate_order_code()
    return code



def update_item_quantity(item_id,quantity):
    item=Item.query.get(item_id)
    item.quantity=item.quantity-quantity
    db.session.commit()
    return 

def delete_cart(cart_id):
    cart=Cart.query.get(cart_id)
    db.session.delete(cart)
    db.session.commit()
    return

@app.route('/get_orders',methods=['GET'])
def get_orders():
    sellers_orders=Order.query.filter_by(seller_id=current_user.id).all()
    buyers_orders=Order.query.filter_by(buyer_id=current_user.id).all()
    seller_items=[]
    buyer=[]
    for item in sellers_orders:
        i=Item.query.get(item.item_bought)
        user=User.query.get(item.buyer_id)
        buyer.append(user)
        seller_items.append(i)
    buyer_items=[]
    for item in buyers_orders:
        i=Item.query.get(item.item_bought)
        buyer_items.append(i)
    bl=len(buyer_items)
    sl=len(seller_items)
    return render_template('orders_list.html',buyer=buyer,bl=bl,sl=sl,
    sellers_orders=sellers_orders,buyers_orders=buyers_orders,seller_items=seller_items,buyer_items=buyer_items)

@app.route("/checkout/<int:id>",methods=['GET'])
@login_required
def checkout(id):
    user=User.query.get(id)
    for c in user.cart:
        item=Item.query.get(c.item_id)
        cart=Cart.query.get(c.cart_id)
        code=generate_order_code()
        newOrder=Order(seller_id=item.user.id,buyer_id=user.id,item_bought=c.item_id,quantity_bought=cart.cart_quantity,
        order_code=code)
        update_item_quantity(c.item_id,cart.cart_quantity)
        delete_cart(c.cart_id)
        db.session.add(newOrder)
    db.session.commit()
    return redirect(url_for('index'))


@app.route("/buyer_order/<int:id>",methods=['GET'])
@login_required
def buyer_order(id):
    order=Order.query.get(id)
    item=Item.query.get(order.item_bought)
    seller=User.query.get(order.seller_id)
    return render_template('buyer_order.html',order=order,item=item,seller=seller)

@app.route("/seller_order/<int:id>",methods=['GET'])
@login_required
def seller_order(id):
    order=Order.query.get(id)
    item=Item.query.get(order.item_bought)
    buyer=User.query.get(order.buyer_id)
    return render_template('seller_order.html',order=order,item=item,buyer=buyer)

def getcode(id):
    order=Order.query.get(id)
    return order.order_code

def deleteorder(id):
    order=Order.query.get(id)
    db.session.delete(order)
    db.session.commit()
    return


@app.route("/confirm_order/<int:id>",methods=['POST'])
def confirm_order(id):
    data=request.form
    submitted_code=data['ordercode']
    code=getcode(id)
    if submitted_code==code:
        deleteorder(id)
        return ("<h1>Order Confirmed<h1>")
    else:
        flash("Incorrect Code")
        return redirect(url_for('get_orders'))

@app.route('/paynow',methods=['POST'])
#@login_required
def paynow():
    checkout={
    "user": [
        {
            "location": {
                "longitude ": 10.643411,
                "latitude": -61.400344
            }
        }
     ],
    "payment_method": "Cash",
    "delivery_option": "Pickup"
    }

    return checkout,201

@app.route('/order_list',methods=['GET'])
#@login_required
def order_list():
    order_list={
    "user": [
        {
            "user_id": 4,
            "username": "Bob",
            "email": "bobross@Mail.com",
            "password": "bobcanpaint123",
            "phone_number": 1234567,
            "location": {
                "longitude ": 10.643411,
                "latitude": -61.400344
            }
        }
        ],
        "orders": [
            {
                "item_id": 1,
                "name": "mango",
                "price": "$3 per",
                "image": "mango.png",
                "quantity": 5
            }
        ],
    }
    return order_list




@app.route('/map',methods=['GET'])
def map():

    map=folium.Map(location=[10.3144,-61.4087],tiles='Stamen Terrain',zoom_start=10)
    users=User.query.all()
    for user in users:
        folium.Marker([user.latitude,user.longtitude],popup=user.username,tooltip=user.username + "'s location "

        ).add_to(map)
    
    return map._repr_html_()


@app.route('/user_location/<int:id>',methods=['GET'])
def user_location(id):
    user=User.query.get(id)
    map=folium.Map(location=[user.latitude,user.longtitude],tiles='Stamen Terrain',zoom_start=10)
    folium.Marker([user.latitude,user.longtitude],popup=user.username,tooltip=user.username + "'s location ").add_to(map)
    return map._repr_html_()




if __name__=="__main__":
    app.run(debug=True)