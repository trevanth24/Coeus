from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from coeus import db, bcrypt
from coeus.models import User, Post
from coeus.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                   RequestResetForm, ResetPasswordForm)
from coeus.users.utils import save_picture, send_reset_email

users = Blueprint('users', __name__)

@users.route('/register', methods = ['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(username = form.username.data, email = form.email.data, password = hashed_pw)
        #Before we add a new user, we want to check if user is already existing in DB. We forward this to a new registrations checker
        db.session.add(new_user)
        db.session.commit()
        flash(f'Your account has been created! You are now able to log in', 'success')
        
        return redirect(url_for('users.login'))
    return render_template('register.html', title = 'Register', form = form)

@users.route('/login', methods = ['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember = form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('main.home'))
        else:
            flash(f'Login Unsuccessful. Please Check Email and Password!', 'danger')
            
    return render_template('login.html', title = 'Login', form = form)

@users.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.home'))



@users.route('/account', methods = ['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data: #Check in the validation if there a new picture update
            #need to save picutre
            picture_filename = save_picture(form.picture.data)
            current_user.image_file = picture_filename

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('users.account'))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename = 'profile_pics/' + current_user.image_file)
    return render_template('account.html', title = 'Account', image_file = image_file, form = form)

@users.route('/user/<string:username>')
def user_posts(username):
    #Pagination
    page = request.args.get('page', 1, type = int) #get args, default page is 1, type is int for page #http://127.0.0.1:5000/home?page=1
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user)\
        .order_by(Post.date_posted.desc())\
        .paginate(per_page = 5, page = page)
    return render_template('user_posts.html', posts=posts, user = user)


@users.route('/reset_password', methods = ['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = RequestResetForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect(url_for('users.login'))
    return render_template('reset_request.html', title='Reset Password', form=form)


@users.route("/reset_password/<token>", methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    user = User.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect(url_for('users.reset_request'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect(url_for('users.login'))
    return render_template('reset_token.html', title='Reset Password', form=form)