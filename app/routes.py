from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from .models import db, User
from .forms import RegistrationForm, LoginForm  # Import your forms
from .extensions import bcrypt


main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)

@main_bp.route('/')
def index():
    return "App successfully created."

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data


        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'danger')
        elif User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
        else:

            user = User(
                username=username,
                email=email,
                name=username
            )
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.login'))

    return render_template('auth/register.html', form=form)  # Pass form to template

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        remember = form.remember.data

        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.hashed_password, password):
            login_user(user, remember=remember)
            flash('Logged in successfully!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('main.index'))

        flash('Invalid username or password', 'danger')

    return render_template('auth/login.html', form=form)  # Pass form to template


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))



@main_bp.route('/dashboard')
@login_required
def dashboard():
    return f"Welcome to your dashboard, {current_user.username}!"