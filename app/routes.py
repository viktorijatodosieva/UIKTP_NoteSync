from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from .models import db, User, Note
from .forms import RegistrationForm, LoginForm, NoteForm  # Import your forms
from .extensions import bcrypt
from datetime import datetime


from .services.ocr_service import OCRService

ocr_service = OCRService()

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

    return render_template('auth/register.html', form=form)

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

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))



@main_bp.route('/dashboard')
@login_required
def dashboard():
    notes = Note.query.filter_by(created_by=current_user.id).all()
    return render_template('dashboard.html', notes=notes)



@main_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_note():
    # form = NoteForm()
    # if form.validate_on_submit():
    #     new_note = Note(
    #         title=form.title.data,
    #         content=form.content.data,
    #         created_by=current_user.id
    #     )
    #     db.session.add(new_note)
    #     db.session.commit()
    #     flash('Note created successfully!', 'success')
    #     return redirect(url_for('main.dashboard'))
    # return render_template('create_note.html', form=form)
    form = NoteForm()
    if form.validate_on_submit():
        content = form.content.data


        if form.image.data:
            extracted_text = ocr_service.extract_text(form.image.data)
            if extracted_text:
                content = extracted_text

        new_note = Note(
            title=form.title.data,
            content=content,
            created_by=current_user.id
        )
        db.session.add(new_note)
        db.session.commit()
        flash('Note created!', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('create_note.html', form=form)



@main_bp.route('/notes')
@login_required
def get_notes():
    notes = Note.query.filter_by(created_by=current_user.id).all()
    return render_template('notes_list.html', notes=notes)


@main_bp.route('/note/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_note(id):
    note = Note.query.get_or_404(id)
    form = NoteForm()

    if form.validate_on_submit():
        note.title = form.title.data
        note.content = form.content.data
        note.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Note updated successfully!', 'success')
        return redirect(url_for('main.dashboard'))

    form.title.data = note.title
    form.content.data = note.content
    return render_template('edit_note.html', form=form, note=note)


@main_bp.route('/note/delete/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_note(id):
    note = Note.query.get_or_404(id)

    if request.method == 'POST':
        db.session.delete(note)
        db.session.commit()
        flash('Note deleted successfully!', 'success')
        return redirect(url_for('main.dashboard'))

    return render_template('delete_note.html', note=note)






