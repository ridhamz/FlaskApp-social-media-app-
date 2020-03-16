from flask import render_template, url_for, flash, redirect, request, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from flaskblog import db, bcrypt
from flaskblog.models import User, Post
from flaskblog.users.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                                   RequestResetForm, ResetPasswordForm)
from flaskblog.users.utils import save_picture, send_reset_email
users = Blueprint('users',__name__)

#Register Page :
@users.route('/register',methods=['GET','POST'])
def register():
     if current_user.is_authenticated:
          return redirect(url_for('home'))
     form = RegistrationForm()
     if form.validate_on_submit():
          hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
          username=form.username.data
          email = form.email.data

          if(User.query.filter_by(username=username).first()):
               flash('username is already exist','danger')
               return render_template('register.html',form=form,title='Register')
          if(User.query.filter_by(email=email).first()):
               flash('Email is already exist','danger')
               return render_template('register.html',form=form,title='Register')

          user = User(username=username,email=email,password=hashed_password)
          db.session.add(user)
          db.session.commit()
          flash('Your account has been created! You are now able to login','success')
          return redirect(url_for('users.login'))
          
     return render_template('register.html',form=form,title='Register')     

#Login Page :
@users.route('/login',methods=['GET','POST'])
def login():
     if current_user.is_authenticated:
          return redirect(url_for('main.home'))
     form = LoginForm()
     if form.validate_on_submit():
          email = form.email.data
          password = form.password.data
          remember = form.remember.data
          user = User.query.filter_by(email=email).first()
          if user and bcrypt.check_password_hash(user.password,password):
               login_user(user,remember=remember)
               next_page = request.args.get('next')
               return redirect(next_page) if next_page else  redirect(url_for('main.home'))
          else:
            flash('Login Unsuccessful  please check your informations','danger')
            return render_template('login.html',form=form,title='Login') 

     return render_template('login.html',form=form,title='Login') 
        
 #log out route :
@users.route('/logout')
def logout():
     logout_user()
     return redirect(url_for('users.login'))

#Account page :
@users.route('/account',methods=['GET','POST'])
@login_required
def account():
          form = UpdateAccountForm()
          if form.validate_on_submit():
               if form.picture.data:
                    picture_file = save_picture(form.picture.data)
                    current_user.img_file = picture_file 
               if current_user.username != form.username.data or current_user.email != form.email.data :
                     current_user.username = form.username.data
                     current_user.email = form.email.data
               if current_user.username != form.username.data or current_user.email != form.email.data or form.picture.data :
                     db.session.commit()
                     flash('Your account has been updated!','success')
               return redirect(url_for('users.account'))
          elif request.method == 'GET':
               form.username.data =  current_user.username  
               form.email.data = current_user.email 
          img_file = url_for('static',filename='profile_pics/'+current_user.img_file)
          return render_template('account.html',title='Account',img_file=img_file,form=form)  
#user posts
@users.route('/user/<string:username>')
def user_posts(username):
     page = request.args.get('page',1,type=int)
     user = User.query.filter_by(username=username).first()
     posts = Post.query.filter_by(auther=user).order_by(Post.date_posted.desc()).paginate(page=page,per_page=2)
     return render_template('user_posts.html',title='Posts',posts=posts,user=user)


@users.route("/reset_password", methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
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
        return redirect(url_for('home'))
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