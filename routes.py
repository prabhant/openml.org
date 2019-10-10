# from flask import Flask, send_from_directory, request, flash
# import os
# from server import app
# from flask_login import current_user, login_user, logout_user
# import models
# from server import db
#
#
# app.route('/', defaults={'path': ''})
# @app.route('/<path:path>')
# def serve(path):
#     if path != "" and os.path.exists("src/client/" + path):
#         return send_from_directory('src/client', path)
#     else:
#         return send_from_directory('src/client', 'index.html')
#
# @app.route('/signup', methods=['POST', 'GET'])
# def signupfunc():
#     if request.method =='POST':
#         print(request.get_json())
#         robj = request.get_json()
#         user = models.User(username=robj['name'], email=robj['email'], password_hash='asdasd')
#         db.session.add(user)
#         db.session.commit()
#
#     return 'request'
#
#
# @app.route('/login', methods=['POST', 'GET'])
# def login():
#     if current_user.is_authenticated:
#         return 'already auth'
#     if request.method =='POST':
#         print(request.get_json())
#         jobj = request.get_json()
#         user = models.User.query.filter_by(username=jobj['email']).first()
#         login_user(user, remember=True)
#         return 'loggedin'
#
# @app.route('/logout')
# def logout():
#     logout_user()
#     return redirect(url_for('index'))