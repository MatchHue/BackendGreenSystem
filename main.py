from ctypes import sizeof
from enum import unique
from gettext import lngettext
import json
from unicodedata import numeric
from xml.etree.ElementTree import tostring
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



@app.context_processor
def base():
    form=SearchForm()
    return dict(form=form)

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
    

class SearchForm(FlaskForm):
    Search=StringField("Search",validators=[DataRequired()])
    submit=SubmitField("Search")

class BulkForm(FlaskForm):
    name=StringField("Username", validators=[DataRequired()])
    quantity=StringField("Quantity", validators=[DataRequired()])
    sort=SelectField("Sort", choices=[("Price"),("Location"),("Rating")])
    checkbox = BooleanField("Multiple")
    submit=SubmitField("Confirm")


#Models

class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String,unique=True,nullable=False)
    pfp=db.Column(db.String,nullable=False)
    email=db.Column(db.String,unique=True,nullable=False)
    phone_number=db.Column(db.Integer,unique=True)
    password=db.Column(db.String,nullable=False)
    longtitude=db.Column(db.Float,nullable=False)
    latitude=db.Column(db.Float,nullable=False)
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

class Bulk(db.Model):
    bulk_id=db.Column(db.Integer,primary_key=True)
    quantity_bought=db.Column(db.Integer,nullable=False)

def getlocation():
    response=requests.get("http://ip-api.com/json/")
    data=response.json()
    return data

@app.route('/',methods=['GET'])
def index():
    users=User.query.all()
    items=Item.query.all()
    images=[]
    newitems=[]
    for item in items:
        if item.quantity>0:
            newitems.append(item)
    return render_template('index.html',users=users,items=newitems,images=images)

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
    curr_sellers=[]
    for s in sellers:
        if len(s.items)>0:
            curr_sellers.append(s)
    return render_template('sellers.html',sellers=curr_sellers)


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




from minizinc import Instance, Model, Solver

def get_item_sellers(items):
    usernames=[]
    for item in items:
        usernames.append(item.user_id)
    return usernames

def get_item_quantities(items):
    quantities=[]
    for item in items:
        quantities.append(item.quantity)
    return quantities

def get_items_prices(items):
    prices=[]
    for item in items:
        prices.append(int(item.price))
    return prices

def get_users_selected(usernames,selected):
    users=[]
    for i in range(len(selected)):
        if selected[i]>0:
            users.append(usernames[i])
    return users

def get_selected_items(items,selected):
    item=[]
    for i in range(len(selected)):
        if selected[i]>0:
            item.append(items[i])
    return item

def selected_selected(selected):
    select=[]
    for i in range(len(selected)):
        if selected[i]>0:
            select.append(selected[i])
    return select


def bulk_logic(items,quantites,prices,usernames,quantity):

   # items=get_items("pumpkin")
    #usernames=get_item_sellers(items)
    #quantites=get_item_quantities(items)
     # prices=get_items_prices(items)
    # Load Bulk_purchase model from file
    bulkorder = Model("./bulkorder.mzn")
    # Find the MiniZinc solver configuration for coin-bc
    gecode = Solver.lookup("coin-bc")
    # Create an Instance of the Bulk_purchase model for coin-bc
    instance = Instance(gecode, bulkorder)
    # Assign 4 to n
    instance["n"] = len(quantites)
    instance["ProduceQuantity"]=quantites
    instance["Prices"]=prices
    instance["quantity"]=quantity
    result = instance.solve()
    # Output the results
    return result


def get_items(item_name):
    items=Item.query
    items=items.filter(Item.name.like('%' + item_name+'%'))
    return items



import math

def convert_to_km(lat1,lon1,lat2,lon2):
    #radius of earth in km
    R=6371
    #lat1=10.315049
    #lon1=-61.431314
    #lat2=10.632447
    #lon2=-61.429257
    phi1=lat1*math.pi/180
    phi2=lat2*math.pi/180
    deltalat=(lat2-lat1)*math.pi/180
    deltalon=(lon2-lon1)*math.pi/180

    a=math.sin(deltalat/2)*math.sin(deltalat/2)+math.cos(phi1)*math.cos(phi2)*math.sin(deltalon/2)*math.sin(deltalon/2)
    c=2*math.atan2(math.sqrt(a),math.sqrt(1-a))

    #distance between both users in km
    d=R*c
    return d

def bulk_by_location(sellerslocation,quantity,quantites):
    
    bulkorder = Model("./bulkorderlocation.mzn")
    # Find the MiniZinc solver configuration for coin-bc
    gecode = Solver.lookup("coin-bc")
    # Create an Instance of the Bulk_purchase model for coin-bc
    instance = Instance(gecode, bulkorder)
    # Assign 4 to n
    instance["n"] = len(quantites)
    instance["ProduceQuantity"]=quantites
    instance["DistanceBetween"]=sellerslocation
    instance["quantity"]=quantity
    result = instance.solve()
    # Output the results
    return result    

@app.route('/bulk_purchase',methods=['GET','POST'])
@login_required
def bulk_purchase():
    items=Item.query.all()
    unique=[]
    for item in items:
        if item.name not in unique:
            unique.append(item.name)
    form=BulkForm()
    if request.method=="POST":
        item1=request.form.get('select1')
        quantity1=request.form.get('quantity1')
        item2=request.form.get('select2')
        quantity2=request.form.get('quantity2')
        item3=request.form.get('select3')
        quantity3=request.form.get('quantity3')
        litems=[]
        lquantities=[]

        if item1!='Select item':
            litems.append(item1)
            lquantities.append(quantity1)
        
        if item2!='Select item':
            litems.append(item2)
            lquantities.append(quantity2)

        if item3!='Select item':
            litems.append(item3)
            lquantities.append(quantity3)

        sort=request.form.get('sort')
        itemsfromitem=[]
        quantitesfromquantity=[]
        quantitesfromquantity=lquantities
        listofitems=[]
        listofselected=[]
        iterations=0

        for i in litems:
            itemsfromitem.append(i)
        iter=len(litems)

        if sort=="Price":
            for i in range(iter):
                item=itemsfromitem[i]
                quantity=quantitesfromquantity[i]
                
                items=get_items(item)
                usernames=get_item_sellers(items)
                quantites=get_item_quantities(items)
                prices=get_items_prices(items)
                Sum=sum(quantites)
                if int(quantity)>Sum:
                    message="Error cannot query order as given quantity of "+ item +" is greater than the quantity avaiable. Available quantity: " + str(Sum) + "kg"
                    flash(message)
                    return redirect(url_for('bulk_purchase'))
                #getting items from miniinc module
                results=bulk_logic(items,quantites,prices,usernames,int(quantity))

                selected=results["SelectedProduces"]
                users=get_users_selected(usernames,selected)
                selected_items=get_selected_items(items,selected)
                select=selected_selected(selected)
                for i in selected_items:
                    listofitems.append(i)
                for i in select:
                    listofselected.append(i)
                iterations=iterations+len(select)

            totalcost=0
            for i in range(iterations):
                totalcost=totalcost+listofitems[i].price*listofselected[i]

            return render_template('bulk_query.html',items=listofitems,select=listofselected,iterations=iterations,totalcost=totalcost)


        if sort=="Location":
            buyer=current_user

            for i in range(iter):
                item=itemsfromitem[i]
                quantity=quantitesfromquantity[i]

                items=get_items(item)
                usernames=get_item_sellers(items)
                quantities=get_item_quantities(items)
                
                locationsinkm=[]
                for i in items:
                    converted=convert_to_km(buyer.latitude,buyer.longtitude,i.user.latitude,i.user.longtitude)
                    locationsinkm.append(converted)
                Sum=sum(quantities)
                if int(quantity)>Sum:
                    message="Error cannot query order as given quantity of "+ item +" is greater than the quantity avaiable. Available quantity: " + str(Sum) + "kg"
                    flash(message)
                    return redirect(url_for('bulk_purchase'))
                #getting items from miniinc module

                results=bulk_by_location(locationsinkm,int(quantity),quantities)
                selected=results["SelectedProduces"]
                selected_items=get_selected_items(items,selected)
                select=selected_selected(selected)
                for i in selected_items:
                    listofitems.append(i)
                for i in select:
                    listofselected.append(i)
            iterations=len(listofitems)

            totalcost=0
            for i in range(iterations):
                totalcost=totalcost+listofitems[i].price*listofselected[i]

            return render_template('bulk_query.html',items=listofitems,select=listofselected,iterations=iterations,totalcost=totalcost)
    
    return render_template('bulk_purchase.html', form=form, items=unique)

@app.route("/add_bulk_to_cart/<int:itemid>/<int:selected>",methods=["GET"])
def add_bulk_to_cart(itemid,selected):
    user=current_user.id
    cartItem=Cart(item_id=itemid,cart_quantity=selected,user_id=user)
    db.session.add(cartItem)
    db.session.commit()
    return ('',204)



@app.route('/search',methods=['GET'])
def search():
    data=request.args.get('searched')
    items=Item.query
    items=items.filter(Item.name.like('%' + data+'%'))
    return render_template('search.html',items=items)

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




@app.route('/get_cart',methods=['GET'])
@login_required
def get_cart():
    user=User.query.get(current_user.id)
    items=[]
    cartitems=[]
    carts=Cart.query.all()
    for c in user.cart:
        item=Item.query.get(c.item_id)
        cart=Cart.query.get(c.cart_id)
        items.append(item)
        cartitems.append(cart)
    l=len(items)
    return render_template('cart.html',items=items,user=user,carts=cartitems,length=l)


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
@login_required
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
        flash("Order Confirmed")
        return redirect(url_for('get_orders'))
    else:
        flash("Incorrect Code")
        return redirect(url_for('get_orders'))





@app.route('/change_location',methods=['GET'])
def change_location():
    return render_template('map.html')

@app.route('/confirm_location',methods=['POST'])
@login_required
def confirm_location():
    req=request.get_json
    lat=req.lat
    lon=req.lng
    flash(lat,lon)
    return render_template('index.html')


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


# OPTIMIZATION 



if __name__=="__main__":
    app.run(debug=True)