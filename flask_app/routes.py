import os
import secrets
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort
from flask_app import app, db, bcrypt, mail
from flask_app.forms import RegistrationForm, LoginForm, UpdateAccountForm, PostForm, RequestResetForm, ResetPasswordForm, SearchForm
from flask_app.models import User, Post
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message
#from shadowd.flask_connector import InputFlask, OutputFlask, Connector

#@app.before_request
#def before_req():
 #   input = InputFlask(request)
 #   output = OutputFlask()

 #   Connector().start(input, output)



@app.route("/") 
@app.route("/home")
@login_required
def home():
	page = request.args.get('page', 1, type=int)
	posts=Post.query.paginate(page=page, per_page=4)
	return render_template('home.html', posts=posts)

#new search functionality added in two new routes below

@app.route("/search", methods=['GET', 'POST'])
@login_required
def search():
	form = SearchForm()
	if request.method == 'POST' and form.validate_on_submit():
		return redirect(url_for('search_results', query=form.search.data))
	return render_template('search.html', form=form)

@app.route('/search_results/<query>')
@login_required
def search_results(query):
	first_result = Post.query.filter_by(last_name=query).first_or_404()
	results = first_result.employee_id
	return render_template('search_results.html', query=query, results=results)

@app.route("/about") 
def about():
	return render_template('about.html', title='About')

def send_register_email_to_admin(email, username, password):

	msg = Message('BloreBank Account Request', sender='flask.webmaster@gmail.com', recipients=['flask.webmaster@gmail.com'])

	msg.body = f'''The following account has been requested for creation:

Email address: {email}
Username: {username}
Password hash: {password}

At your earliest convenience, please login and enter the BloreBank administrative portal; after doing so, you can add this account under the /admin/user endpoint.

If you ignore this email, no account changes will be made.

Regards,
BloreBank Development Team

'''
	mail.send(msg)

@app.route("/register", methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegistrationForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		#hashed_password = form.password.data
		user = form.username.data
		email_of_user = form.email.data
		send_register_email_to_admin(email_of_user, user, hashed_password)
		flash('Submitted! The admin will now review the request.', 'info')
		return redirect(url_for('about'))

	return render_template('register.html', title='Register', form=form)

#Uncomment the below and comment the above register() function should you wish to give unauthenticated users ability to self-register
#def register():
#	if current_user.is_authenticated:
#		return redirect(url_for('home'))
#	form = RegistrationForm()
#	if form.validate_on_submit():
#		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
#		user = User(username=form.username.data, email=form.email.data, password=hashed_password)
#		db.session.add(user)
#		db.session.commit()
#		flash('Account created! Please log in.', 'success')
#		return redirect(url_for('login'))
#
#	return render_template('register.html', title='Register', form=form)

@app.route("/login", methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first() #filtering db to see if the email they input exists
		#now we make conditional to check user exists and password verifies w/ db
		if user and bcrypt.check_password_hash(user.password, form.password.data):
			login_user(user, remember=form.remember.data) #second arg will be true if form checked vice versa
			flash('Login Success!', 'success')
			next_page = request.args.get('next')
			return redirect(next_page) if next_page else redirect(url_for('home'))

		else:
			flash('Login Failed!', 'danger')			

	return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
	logout_user()
	return redirect(url_for('home'))

def save_picture(form_picture):
	random_hex = secrets.token_hex(8)
	_, f_ext = os.path.splitext(form_picture.filename)
	picture_fn = random_hex + f_ext
	picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
	
	output_size = (125, 125)
	i = Image.open(form_picture)
	i.thumbnail(output_size)

	i.save(picture_path) #now we have pic saved on filesystem

	return picture_fn

@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
	form = UpdateAccountForm()
	if form.validate_on_submit():
		if form.picture.data:
			picture_file = save_picture(form.picture.data)
			current_user.image_file = picture_file
#uncomment below 2 lines to give users ability to update profile outside of /admin portal
#		current_user.username = form.username.data
#		current_user.email = form.email.data
		db.session.commit()
		flash('Your account has been updated!', 'success')
		return redirect(url_for('account'))
	elif request.method == 'GET':
		form.username.data = current_user.username
		form.email.data = current_user.email
	image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
	return render_template('account.html', title='Account', image_file=image_file, form=form)

@app.route("/post/new", methods=['GET', 'POST'])
@login_required
def new_post():
	form = PostForm()
	if current_user.username != 'admin' and current_user.username != 'manager':
		abort(403)
	if form.validate_on_submit():
		post = Post(employee_id=form.empl_id.data, first_name=form.first_n.data, last_name=form.last_n.data, birthday=form.b_day.data, address=form.addr.data, contact_number=form.contact.data, position=form.pos.data, intranet_user=form.int_user.data, intranet_pass=form.int_pass.data, author=current_user)
		db.session.add(post)
		db.session.commit()
		flash('The record has been created!', 'success')
		return redirect(url_for('home'))
	return render_template('create_post.html', title='New Post', 
							form=form, legend='Create New Employee Record')

@app.route("/post/<int:post_id>")
@login_required
def post(post_id):
	post = Post.query.get_or_404(post_id)
	return render_template('post.html', post=post)

@app.route("/post/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_post(post_id):
	post = Post.query.get_or_404(post_id)
	if current_user.username != 'admin' and current_user.username != 'manager':
		abort(403)
	form = PostForm()
	if form.validate_on_submit():
		post.employee_id = form.empl_id.data
		post.first_name = form.first_n.data
		post.last_name = form.last_n.data
		post.birthday = form.b_day.data
		post.address = form.addr.data
		post.contact_number = form.contact.data
		post.position = form.pos.data
		post.intranet_user = form.int_user.data
		post.intranet_pass = form.int_pass.data
		db.session.commit()
		flash('The record has been updated!', 'success')
		return redirect(url_for('post', post_id=post.employee_id)) 

	elif request.method == 'GET':
		form.empl_id.data = post.employee_id
		form.first_n.data = post.first_name
		form.last_n.data = post.last_name
		form.b_day.data = post.birthday
		form.addr.data = post.address
		form.contact.data = post.contact_number
		form.pos.data = post.position
		form.int_user.data = post.intranet_user
		form.int_pass.data = post.intranet_pass

	return render_template('create_post.html', title='Update Post', 
							form=form, legend='Update Employee Record')

@app.route("/post/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_post(post_id):
	post = Post.query.get_or_404(post_id)
	if current_user.username != 'admin' and current_user.username != 'manager':
		abort(403)
	db.session.delete(post)
	db.session.commit()
	flash('The record has been deleted!', 'success')
	return redirect(url_for('home'))

def send_reset_email(user):
	token = user.get_reset_token() #leaving seconds of 900 as default
	msg = Message('Password Reset Request - BloreBank', sender='flask.webmaster@gmail.com', recipients=[user.email])

	#note - we need _external arg below to render an absolute link not a relative one

	msg.body = f'''To reset your password, visit the following link:

{url_for('reset_token', token=token, _external=True)}

If you did not make this request, please ignore this email and no changes will be made.

'''
	mail.send(msg)

@app.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RequestResetForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		send_reset_email(user)
		flash('An email has been sent with password reset instructions', 'info')
		return redirect(url_for('login'))
	return render_template('reset_request.html', title='Reset Password', form=form)

@app.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	user = User.verify_reset_token(token)	#recall this should return user id from models.py
	if user is None:
		flash('That is an invalid or expired token!', 'warning')
		return redirect(url_for('reset_request'))
	#if we make it to here token was valid and user can reset their password
	form = ResetPasswordForm()
	if form.validate_on_submit():
		hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
		user.password = hashed_password
		db.session.commit()
		flash(f'Password updated! Please log in.', 'success')
		return redirect(url_for('login'))
	return render_template('reset_token.html', title='Reset Password', form=form)