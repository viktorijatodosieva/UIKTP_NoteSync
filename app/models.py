from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    hashed_password = db.Column(db.String, nullable=False)
    name = db.Column(db.String, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    notes = db.relationship('Note', back_populates='user', cascade='all, delete-orphan')
    notifications = db.relationship('Notification', back_populates='user', cascade='all, delete-orphan')
    user_notes = db.relationship('UserHasAccessNote', back_populates='user', cascade='all, delete-orphan')


class Note(db.Model):
    __tablename__ = 'note'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.Text)
    created_by = db.Column(db.String, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship('User', back_populates='notes')
    notifications = db.relationship('Notification', back_populates='note', cascade='all, delete-orphan')
    user_access = db.relationship('UserHasAccessNote', back_populates='note', cascade='all, delete-orphan')
    note_tags = db.relationship('NoteBelongsToTag', back_populates='note', cascade='all, delete-orphan')


class Notification(db.Model):
    __tablename__ = 'notification'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String, db.ForeignKey('user.id'))
    title = db.Column(db.String)
    description = db.Column(db.Text)
    is_read = db.Column(db.Boolean, default=False)
    note_id = db.Column(db.Integer, db.ForeignKey('note.id'))
    referenced_user_id = db.Column(db.String, db.ForeignKey('user.id'))
    type = db.Column(db.String)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship('User', back_populates='notifications')
    note = db.relationship('Note', back_populates='notifications')


class Tag(db.Model):
    __tablename__ = 'tag'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.Text)
    created_by = db.Column(db.String, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    note_tags = db.relationship('NoteBelongsToTag', back_populates='tag', cascade='all, delete-orphan')


class UserHasAccessNote(db.Model):
    __tablename__ = 'user_has_access_note'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String, db.ForeignKey('user.id'))
    note_id = db.Column(db.Integer, db.ForeignKey('note.id'))
    shared_by = db.Column(db.String, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship('User', back_populates='user_notes')
    note = db.relationship('Note', back_populates='user_access')


class NoteBelongsToTag(db.Model):
    __tablename__ = 'note_belongs_to_tag'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    note_id = db.Column(db.Integer, db.ForeignKey('note.id'))
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))
    is_private = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    note = db.relationship('Note', back_populates='note_tags')
    tag = db.relationship('Tag', back_populates='note_tags')
