from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
db = SQLAlchemy()

def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class User(db.Model):
    """User table parameters"""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.Text, default="/static/images/default-pic.png")



    @classmethod
    def signup(cls, email, username, password, image_url):
        """Sign up user.

        Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
        )

        db.session.add(user)
        return user

    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False

class UserTeam(db.Model):
    """User's saved team that will display the user's
    fantasy team and show statistics and link to player pages"""

    __tablename__ = "users_team"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
        )
    player_id = db.Column(
        db.Integer,
        db.ForeignKey('players.id', ondelete='CASCADE'),
        nullable=False,
        )
## player_stats: here is where i dont want to get each stat, 
# rather import a specific data set that is made by the api to be saved

    user = db.relationship('User')
    player = db.relationship('Player')


class Player(db.Model):
    """Table containing reference to requested players list."""

    __tablename__ = 'players'

    id = db.Column(db.Integer, primary_key=True)## value to be player id value on api
    ## player_stats: here is where i dont want to get each stat, 
# rather import a specific data set that is made by the api to be saved save as jsonfield
    first_name = db.Column(db.Text())
    last_name = db.Column(db.Text())
    full_name = db.Column(db.Text())

    team = db.relationship('Team', backref='players')

class Season(db.Model):
    """NBA Seaons tables"""
    __tablename__ = 'seasons'

    id = db.Column(db.Integer, primary_key=True)
    season = db.Column(db.Integer, default="2022")
    

    player = db.relationship('Player')
    team = db.relationship('Team')

class Team(db.Model):
    """List of teams"""
    __tablename__ ="teams"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text())
    abbr = db.Column(db.Text())

    player = db.relationship('Player')
    