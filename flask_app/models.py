from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask_app import db, login_manager, app
from flask_login import UserMixin

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(20), unique=True, nullable=False)
	email = db.Column(db.String(120), unique=True, nullable=False)
	image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
	password = db.Column(db.String(60), nullable=False)
	posts = db.relationship('Post', backref='author', lazy=True)

	def get_reset_token(self, expires_sec=900):
		s = Serializer(app.config['SECRET_KEY'], expires_sec)
		return s.dumps({'user_id': self.id}).decode('utf-8')

	@staticmethod
	def verify_reset_token(token):
		s = Serializer(app.config['SECRET_KEY'])
		try:
			user_id = s.loads(token)['user_id']
		except:
			return None
		return User.query.get(user_id)

	def __repr__(self):
		return f"User('{self.username}', '{self.email}', '{self.image_file}')"

class Post(db.Model):
	__searchable__ = ['last_name']
	employee_id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String(120), unique=True, nullable=False)
	last_name = db.Column(db.String(120), unique=True, nullable=False)
	birthday = db.Column(db.String(10), nullable=False)
	address = db.Column(db.String(120), nullable=False)
	contact_number = db.Column(db.String(20), unique=True, nullable=False)
	position = db.Column(db.String(120), nullable=False)
	intranet_user = db.Column(db.String(30), unique=True, nullable=False)
	intranet_pass = db.Column(db.String(30), nullable=False)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

	def __repr__(self):
		return f"User('{self.employee_id}', '{self.first_name}', '{self.last_name}')"
