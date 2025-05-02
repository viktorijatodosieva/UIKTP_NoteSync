from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_bcrypt import Bcrypt
from flask_login import UserMixin
from .extensions import db, bcrypt


class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    hashed_password = db.Column(db.String(128), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    notes = db.relationship('Note', back_populates='user', cascade='all, delete-orphan')
    notifications = db.relationship(
        'Notification',
        foreign_keys='[Notification.user_id]',
        back_populates='user',
        cascade='all, delete-orphan'
    )
    shared_notes = db.relationship(
        'UserHasAccessNote',
        foreign_keys='[UserHasAccessNote.user_id]',
        back_populates='user',
        cascade='all, delete-orphan'
    )
    notes_shared_by_me = db.relationship(
        'UserHasAccessNote',
        foreign_keys='[UserHasAccessNote.shared_by]',
        back_populates='sharer'
    )

    def set_password(self, password):
        self.hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.hashed_password, password)


class Note(db.Model):
    __tablename__ = 'note'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship('User', back_populates='notes')
    notifications = db.relationship('Notification', back_populates='note', cascade='all, delete-orphan')
    shared_with = db.relationship('UserHasAccessNote', back_populates='note', cascade='all, delete-orphan')
    note_tags = db.relationship('NoteBelongsToTag', back_populates='note', cascade='all, delete-orphan')


class Notification(db.Model):
    __tablename__ = 'notification'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    is_read = db.Column(db.Boolean, default=False)
    note_id = db.Column(db.Integer, db.ForeignKey('note.id'))
    referenced_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    type = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship('User', foreign_keys=[user_id], back_populates='notifications')
    note = db.relationship('Note', back_populates='notifications')
    referenced_user = db.relationship('User', foreign_keys=[referenced_user_id])

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'is_read': self.is_read,
            'note_id': self.note_id
        }


class Tag(db.Model):
    __tablename__ = 'tag'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), nullable=False, unique=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    note_tags = db.relationship('NoteBelongsToTag', back_populates='tag', cascade='all, delete-orphan')


class UserHasAccessNote(db.Model):
    __tablename__ = 'user_has_access_note'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    note_id = db.Column(db.Integer, db.ForeignKey('note.id'))
    shared_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship('User', foreign_keys=[user_id], back_populates='shared_notes')
    sharer = db.relationship('User', foreign_keys=[shared_by], back_populates='notes_shared_by_me')
    note = db.relationship('Note', back_populates='shared_with')


class NoteBelongsToTag(db.Model):
    __tablename__ = 'note_belongs_to_tag'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    note_id = db.Column(db.Integer, db.ForeignKey('note.id'))
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'))
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    note = db.relationship('Note', back_populates='note_tags')
    tag = db.relationship('Tag', back_populates='note_tags')