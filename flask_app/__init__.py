from flask import Flask
from flask import url_for, flash, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin #new
from flask_admin.contrib.sqla import ModelView #new
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, current_user, AnonymousUserMixin #added AnonymousUserMixin
from flask_mail import Mail

app = Flask(__name__) #name of module
app.config['SECRET_KEY'] = '89d6310cdb1c71ace694d9864540b18a'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'flask.webmaster@gmail.com'
app.config['MAIL_PASSWORD'] = 's3creth@xorp@sswordforreal&72qq'
mail = Mail(app)

class Anonymous(AnonymousUserMixin):
	def __init__(self):
		self.username = 'Guest'

login_manager.anonymous_user = Anonymous #new

class MyModelView(ModelView):
	def is_accessible(self):
		if current_user.username == 'admin' or current_user.username == 'manager':	
			return current_user.is_authenticated
		elif current_user.username == 'Anonymous': #catching error of anon user not having username attrib prev mapped
			return False
		else:									   #else user is logged in but not admin
			return False 

from flask_app.models import User, Post

admin = Admin(app)

admin.add_view(MyModelView(User, db.session))
admin.add_view(MyModelView(Post, db.session))

from flask_app import routes