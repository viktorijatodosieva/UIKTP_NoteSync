from functools import wraps
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from .models import Note
from flask_login import current_user

def creator_or_shared_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        note_id = kwargs.get('id')
        note = Note.query.get_or_404(note_id)
        if int(note.created_by) != int(current_user.id) and not any(int(a.user_id) == int(current_user.id) for a in note.shared_with):
            flash("You don't have access to this note.", 'danger')
            return redirect(url_for("main.get_notes"))
        return f(*args, **kwargs)
    return decorated_function

def creator_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        note_id = kwargs.get('id')
        note = Note.query.get_or_404(note_id)
        if int(note.created_by) != int(current_user.id):
            flash("You are not the creator of this note.", 'danger')
            return redirect(url_for("main.get_notes"))
        return f(*args, **kwargs)
    return decorated_function
