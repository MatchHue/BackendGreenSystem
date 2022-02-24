from flask import Flask, render_template,request,redirect,url_for,redirect,jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField,SubmitField, PasswordField, BooleanField, ValidationError,EmailField, DecimalField, SelectField,IntegerField,FloatField
from wtforms.validators import DataRequired, EqualTo, Length
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, login_manager, login_required, logout_user, current_user, LoginManager
import os
from flask_simple_geoip import SimpleGeoIP


app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///test.db'
app.config['SECRET_KEY']='CharizardIsTheBestStarter'
app.config.update(GEOIPIFY_API_KEY='at_fK21skNWFKsJzxSdjKIvKvpbc4IQU    ')

db=SQLAlchemy(app)


simple_geoip = SimpleGeoIP(app)


#Login Setup
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view='login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))





class LoginForm(FlaskForm):
    email=EmailField("Email",validators=[DataRequired()])
    password=PasswordField("Password",validators=[DataRequired()])
    submit=SubmitField("Login")

class SignUpForm(FlaskForm):
    username=StringField("Username",validators=[DataRequired()])
    email=EmailField("Email",validators=[DataRequired()])
    phone_number=StringField("Contact",validators=[DataRequired()])
    password=PasswordField("Password",validators=[DataRequired()])
    longtitude=DecimalField("longtitude",validators=[DataRequired()])
    latitude=DecimalField("latitude",validators=[DataRequired()])
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
    email=db.Column(db.String,unique=True,nullable=False)
    phone_number=db.Column(db.Integer,unique=True)
    password=db.Column(db.String,nullable=False)
    longtitude=db.Column(db.Numeric,nullable=False)
    latitude=db.Column(db.Numeric,nullable=False)
    #items=db.relationship('Item',backref='user')


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
    #user_id=db.Column(db.Integer,db.ForeignKey('user.id'))s
    name=db.Column(db.String,nullable=False)
    image=db.Column(db.String,nullable=False)
    #image_name=db.Column(db.String,nullable=False)
    #mimetype=db.Column(db.String,nullable=False)
    quantity=db.Column(db.Integer,nullable=False)
    price=db.Column(db.Float,nullable=False)
    delivery=db.Column(db.String,nullable=False)
    #cart_items=db.relationship('Item',backref='item')


    def toDict(self):
        return{
            'id': self.id,
            'name': self.name,
            'image':self.image,
            'quantity': self.quantity,
            'price':self.price
        }




@app.route('/',methods=['GET'])
def index():
    users=User.query.all()
    items=Item.query.all()
    images=[]
    for item in items:
        images.append(url_for('static',filename='item_images/+item.image'))
    return render_template('index.html',users=users,items=items,images=images)

@app.route('/test',methods=['GET'])
def testroute():
    geoip_data = simple_geoip.get_geoip_data()
    return geoip_data


@app.route('/signup',methods=['GET','POST'])
def signup():
    form=SignUpForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user is None:
            newUser=User(username=form.username.data,email=form.email.data,password=form.password.data,
            phone_number=form.phone_number.data,
            longtitude=form.longtitude.data,latitude=form.latitude.data)
            newUser.set_password(newUser.password)
            db.session.add(newUser)
            db.session.commit()
        form.username.data=''
        form.email.data=''
        return redirect(url_for('index'))
    return render_template('signup.html',form=form)

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


@app.route('/get_user_items',methods=['GET'])
def get_user_items():
    user_item= {
    "user_id": 2,
    "email": "matthew234@mail.com",
    "username": "Matthew",
    "items": [
        {
            "item_id": 1,
            "name": "pumpkin",
            "price": "6$ per pound",
            "image": "pumpkin.png",
            "quantity": "40lbs"
        },
        {
            "item_id": 2,
            "name": "mango",
            "price": "$3 per",
            "image": "mango.png",
            "quantity": 20
        }
    ]
}
    return user_item


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
        image_file=saveimage(form.image.data)
        print(image_file)
        newItem=Item(name=form.name.data,image=image_file,quantity=form.quantity.data,price=form.price.data,
        delivery=form.delivery.data)
        db.session.add(newItem)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('listitem.html',form=form)


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

@app.route('/add_to_cart',methods=['POST'])
#@login_required
def add_to_cart():
    cart={
    "item_id": 1,
    "name": "mango",
    "price": "$3 per",
    "image": "mango.png",
    "quantity": 5
    }

    return jsonify(message='Item added'),cart

@app.route('/checkout',methods=['POST'])
#@login_required
def checkout():
    cart={
        item:{
        "name":"mango",
        "price":"$3 per",
        "image":"mango.png",
        "quantity":15
        }
        }
    return cart,200

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

@app.route('/confirm_order',methods=['POST'])
#@login_required
def confirm_order():
    return jsonify(message='Order Confirmed')

@app.route('/map',methods=['GET'])
def map():
    locations= {
            "location": {
                "longitude ": 10.643411,
                "latitude": -61.400344
            }}
    return locations

if __name__=="__main__":
    app.run(debug=True)