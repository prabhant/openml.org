from flask import Flask, request
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_login import LoginManager, login_user, current_user,logout_user
import os
import requests

app = Flask(__name__, static_url_path='', static_folder='src/client/app/build',
            instance_relative_config=True)

app.config.from_object(Config)
#CORS initialisation
CORS(app)
#Login initialisation
loginmgr = LoginManager(app)
loginmgr.init_app(app)
loginmgr.login_view = 'login'

#Database initialisation
db = SQLAlchemy(app)
migrate = Migrate(app, db)

import routes, models

app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    if path != "" and os.path.exists("src/client/" + path):
        return send_from_directory('src/client', path)
    else:
        return send_from_directory('src/client', 'index.html')

@app.route('/signup', methods=['POST', 'GET'])
def signupfunc():
    if request.method =='POST':
        print(request.get_json())
        robj = request.get_json()
        user = models.User(username=robj['name'], email=robj['email'], password_hash='asdasd')
        db.session.add(user)
        db.session.commit()

    return 'request'


@app.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return 'already auth'
    if request.method =='POST':
        print(request.get_json())
        jobj = request.get_json()
        user = models.User.query.filter_by(username=jobj['email']).first()
        login_user(user, remember=True)
        return 'loggedin'

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(port=int(os.environ.get("PORT", 5000)), debug=True)


