import os

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort, current_app
from flask_login import login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename

from .models import db, User, Note, UserHasAccessNote, Tag, NoteBelongsToTag
from .forms import RegistrationForm, LoginForm, NoteForm, ShareNoteForm  # Import your forms
from .extensions import bcrypt
from .middleware import creator_or_shared_required, creator_required
from datetime import datetime
from fpdf import FPDF
from flask import make_response


from .services.ocr_service import OCRService

ocr_service = OCRService()
main_bp = Blueprint('main', __name__)
auth_bp = Blueprint('auth', __name__)


@main_bp.route('/')
@login_required
def index():
    notes = Note.query.filter_by(created_by=current_user.id).all()
    return render_template('notes_list.html', notes=notes)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()

    if form.validate_on_submit():
        username = form.username.data
        name = form.name.data
        email = form.email.data
        password = form.password.data

        if User.query.filter_by(username=username).first():
            flash('Username already taken', 'danger')
        elif User.query.filter_by(email=email).first():
            flash('Email already registered', 'danger')
        else:
            user = User(
                name=name,
                username=username,
                email=email,
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


@main_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_note():
    form = NoteForm()

    if form.validate_on_submit():
        content = form.content.data or ""
        image_path = None
        raw_text = None

        uploaded_file = form.file.data

        if uploaded_file:
            filename = secure_filename(uploaded_file.filename)
            extension = filename.rsplit('.', 1)[-1].lower()

            uploaded_file.seek(0)

            if extension in ['png', 'jpg', 'jpeg']:
                raw_text = ocr_service.extract_raw_text(uploaded_file)
                corrected_text = ocr_service.correct_text(raw_text)

                uploaded_file.seek(0)
                image_path = os.path.join('static', 'images', filename)
                full_image_path = os.path.join(current_app.root_path, image_path)
                uploaded_file.save(full_image_path)

                if corrected_text:
                    raw_text = corrected_text

            elif extension == 'txt':
                try:
                    file_content = uploaded_file.read()
                    raw_text = file_content.decode('utf-8')
                except UnicodeDecodeError:
                    uploaded_file.seek(0)
                    raw_text = uploaded_file.read().decode('latin-1')

            else:
                flash('Unsupported file type. Only image files (PNG, JPG, JPEG) and .txt files are allowed.', 'danger')
                return redirect(url_for('main.create_note'))

        if raw_text:
            content = raw_text.strip()

        new_note = Note(
            title=form.title.data,
            content=content,
            created_by=current_user.id
        )
        db.session.add(new_note)
        db.session.commit()
        flash('Note created successfully!', 'success')
        return redirect(url_for('main.edit_note', id=new_note.id))

    return render_template('create_note.html', form=form)


@main_bp.route('/notes')
@login_required
def get_notes():
    notes = Note.query.filter_by(created_by=current_user.id).all()
    return render_template('notes_list.html', notes=notes)

@main_bp.route('/wikinote',methods=['GET', 'POST'])
@login_required
def get_wikinote():
    form = NoteForm()
    if form.validate_on_submit():
        content = form.content.data

        if form.image.data:
            extracted_text = ocr_service.extract_text(form.image.data)
            if extracted_text:
                content = content + '\n' + extracted_text

        new_note = Note(
            title=form.title.data,
            content=content,
            created_by=current_user.id
        )
        db.session.add(new_note)
        db.session.commit()
        flash('Note created successfully!', 'success')
        return redirect(url_for('main.index'))
    notes = Note.query.filter_by(created_by=current_user.id).all()
    return render_template('wikinote.html', notes=notes, form=form)


@main_bp.route('/notes/shared-with-me')
@login_required
def get_shared_notes():
    notes = (
        db.session.query(Note)
        .join(UserHasAccessNote)
        .filter(UserHasAccessNote.user_id == current_user.id)
        .all()
    )
    return render_template('shared_notes_list.html', notes=notes)


@main_bp.route('/note/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@creator_or_shared_required
def edit_note(id):
    note = Note.query.get_or_404(id)
    form = NoteForm()

    if form.validate_on_submit():
        note.title = form.title.data
        note.content = form.content.data
        note.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Note updated successfully!', 'success')
        return redirect(url_for('main.index'))

    form.title.data = note.title
    form.content.data = note.content
    return render_template('edit_note.html', form=form, note=note)


@main_bp.route('/note/share/<int:id>', methods=['GET', 'POST'])
@login_required
@creator_or_shared_required
def share_note(id):
    note = Note.query.get_or_404(id)
    form = ShareNoteForm()

    if form.validate_on_submit():
        username = form.user.data
        user = User.query.filter_by(username=username).first()
        if not user:
            flash(f'User "{username}" does not exist.', 'danger')
            return redirect(request.referrer)

        already_shared = UserHasAccessNote.query.filter_by(user_id=user.id, note_id=note.id).first()
        creator = note.created_by == user.id
        if already_shared or creator:
            flash(f'Note already shared with {username}', 'warning')
            return redirect(request.referrer)

        access = UserHasAccessNote(user_id=user.id, note_id=note.id, shared_by=current_user.id)
        note.shared_with.append(access)

        db.session.commit()
        flash(f'Note shared with {username}', 'success')
        return redirect(request.referrer)

    return render_template('share_note.html', form=form, note=note)


@main_bp.route('/note/<int:id>', methods=['GET'])
@login_required
@creator_or_shared_required
def view_note(id):
    note = Note.query.get_or_404(id)
    tags_id_for_note = [tag_note.tag_id for tag_note in note.note_tags]
    all_tags_by_user = Tag.query.filter_by(created_by=current_user.id).all()
    tags_for_note_by_user = [tag for tag in all_tags_by_user if tag.id in tags_id_for_note]

    return render_template('view_note.html', note=note, tags_for_note_by_user=tags_for_note_by_user, all_tags_by_user=all_tags_by_user)


@main_bp.route('/note/delete/<int:id>', methods=['GET', 'POST'])
@login_required
@creator_required
def delete_note(id):
    note = Note.query.get_or_404(id)

    if request.method == 'POST':
        db.session.delete(note)
        db.session.commit()
        flash('Note deleted successfully!', 'success')
        return redirect(url_for('main.index'))

    return render_template('delete_note.html', note=note)

@main_bp.route('/note/<int:id>/add_tag', methods=['POST'])
def add_tag_to_note(id):
    note = Note.query.get_or_404(id)
    tag_input = request.form.get('tag')

    tag_existing_for_user = Tag.query.filter_by(created_by=current_user.id, name=tag_input).all()
    if not tag_existing_for_user:
        tag = Tag(name=tag_input, created_by=current_user.id)
        db.session.add(tag)
        db.session.commit()
    else:
        tag = tag_existing_for_user[0]

    if tag not in note.note_tags:
        note_tag = NoteBelongsToTag(note_id=note.id, tag_id=tag.id)
        note.note_tags.append(note_tag)
        db.session.commit()

    flash(f'Note successfully tagged as {tag_input}.', 'success')
    return redirect(url_for('main.view_note', id=note.id))

@main_bp.route('/note/export/<int:id>')
@login_required
def export_note_pdf(id):
    note = Note.query.get_or_404(id)

    if note.created_by != current_user.id:
        flash('You do not have permission to export this note.', 'danger')
        return redirect(url_for('main.dashboard'))

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, note.title, ln=True, align='C')

    pdf.ln(10)
    pdf.set_font('Arial', '', 12)
    pdf.multi_cell(0, 10, note.content)

    response = make_response(pdf.output(dest='S').encode('latin1'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={note.title}.pdf'

    return response
