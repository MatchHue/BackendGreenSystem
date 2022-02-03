from app.models import Item
from flask import Flask, render_template,request,redirect,url_for,redirect
from flask_sqlalchemy import SQLAlchemy



@app.route('/test',methods=['GET'])
def test():
    return "<h1>HELLO<h1>"

@app.route('/create_item',methods=['POST'])
def create_item():
    data=request.form
    newItem=Item(name=data['name'],quantity=data['quantity'],price=data['price'])
    db.session.add(newItem)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/items',methods=['GET'])
def list_items():
    items=Item.query.all()
    return render_template('product.html',items=items)

@app.route('/sortbyprice',methods=['GET'])
def sort_by_price():
    items=Item.query.order_by('price').asc()
    return render_template('product.html',items=items)
