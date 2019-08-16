from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Email


# Reset password form
class ResetPasswordForm(FlaskForm):
    new_password = PasswordField('Your new Password', validators=[DataRequired()])
    re_new_password = PasswordField('Entry again', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Reset')


# Reset password request form
class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')
