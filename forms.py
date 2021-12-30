from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, TextAreaField
from wtforms.fields.simple import PasswordField
from wtforms.validators import DataRequired, Email, InputRequired, Optional, Length


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('E-mail', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])
    image_url = StringField('(Optional) Image URL')

class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class UserTeamPlayerAdd(FlaskForm):
    """form to add a users fantasy tema to profile"""

    player_name = StringField("Player's Name", validators=[DataRequired()], limit)

class PlayerSearchFrom(FlaskForm):
    """form used to search for specific player"""

    player_name = StringField("Player's Name", validators=[DataRequired()])

