from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Email, Length
from flask_wtf.file import FileField, FileAllowed
from wtforms.fields.simple import SubmitField

class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')

class NoteForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    content = TextAreaField('Content')

    file = FileField('Upload Image or Document', validators=[
        FileAllowed(['jpg', 'png', 'jpeg','txt'], 'Images and Documents only!')
    ])

    submit = SubmitField('Save Note')

class ShareNoteForm(FlaskForm):
    user = StringField('User', validators=[DataRequired()])
