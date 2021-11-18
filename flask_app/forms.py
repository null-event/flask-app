from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_app.models import User

class RegistrationForm(FlaskForm):

	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])

	email = StringField('Email', validators=[DataRequired(), Email()])

	password = PasswordField('Password', validators=[DataRequired()])

	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

	submit = SubmitField('Sign Up')

	def validate_username(self, username):
		user = User.query.filter_by(username=username.data).first()
		if user:
			raise ValidationError('That user already exists!')


	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user:
			raise ValidationError('That email is already registered!')



class LoginForm(FlaskForm):

	email = StringField('Email', validators=[DataRequired(), Email()])

	password = PasswordField('Password', validators=[DataRequired()])

	remember = BooleanField('Remember Me')

	submit = SubmitField('Login')


class UpdateAccountForm(FlaskForm):

	username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])

	email = StringField('Email', validators=[DataRequired(), Email()])

	picture = FileField('Update Picture', validators=[FileAllowed(['jpg', 'png'])])

	submit = SubmitField('Update')

	def validate_username(self, username):
		if username.data != current_user.username:
			user = User.query.filter_by(username=username.data).first()
			if user:
				raise ValidationError('That user already exists!')


	def validate_email(self, email):
		if email.data != current_user.email:
			user = User.query.filter_by(email=email.data).first()
			if user:
				raise ValidationError('That email is already registered!')

class PostForm(FlaskForm):

	empl_id = StringField('ID', validators=[DataRequired()])

	first_n = StringField('First Name', validators=[DataRequired()])

	last_n = StringField('Last Name', validators=[DataRequired()])

	b_day = StringField('DOB', validators=[DataRequired()])

	addr = StringField('Address', validators=[DataRequired()])

	contact = StringField('Contact Number', validators=[DataRequired()])

	pos = StringField('Position', validators=[DataRequired()])

	int_user = StringField('Intranet Username', validators=[DataRequired()])

	int_pass = StringField('Intranet Password', validators=[DataRequired()])

	submit = SubmitField('Create Employee Record')

class RequestResetForm(FlaskForm):

	email = StringField('Email', validators=[DataRequired(), Email()])

	submit = SubmitField('Request Password Reset')

	def validate_email(self, email):
		user = User.query.filter_by(email=email.data).first()
		if user is None:
			raise ValidationError('No account with that email - you must register first.')

class ResetPasswordForm(FlaskForm):

	password = PasswordField('Password', validators=[DataRequired()])

	confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])

	submit = SubmitField('Reset Password')

class SearchForm(FlaskForm):

	search = StringField('Employee Last Name:', validators=[DataRequired()])

	submit = SubmitField('Search')