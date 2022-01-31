from models import (User,db)

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