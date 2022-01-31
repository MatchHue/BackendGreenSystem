from models import (User,db)
from flask import Flask, render_template,request,redirect,url_for,redirect
from flask_sqlalchemy import SQLAlchemy


@app.route('/get_all_users_json',methods=['GET'])
def get_all_users_json():
    users = User.query.all()
    if not users:
        return []
    users = [user.toDict() for user in users]
    return users

@app.rout('/get_all_users',methods=['POST'])
def get_all_users():
    return User.query.all()

@app.route('/signup',methods=['POST'])
def create_user(username,password):
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()


@app.route('/user_items/<username>',methods=['GET'])
def get_user_items(username):
    user_items=User.query.filter_by(username=username).first()
    return render_template('products',user_items=user_items.items)