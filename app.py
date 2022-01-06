from flask import Flask, request, jsonify, render_template, session, flash, redirect, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.elements import Null
from nba_api.stats.library import data, parameters
import pandas as pd
from models import db, connect_db, User, Player, Season, Team, UserTeam
from forms import UserAddForm, LoginForm, UserTeamPlayerAdd, PlayerSearchFrom
from helper import get_player_stats_opponents, get_player_stats_total, get_player_stats_avg, get_lastngames_stats, get_player_stats_location

player_headshot = "https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/" + players_list['id'] + ".png"


CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///nba_stats'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = "p-word-here-shhhhh"

connect_db(app)

players_list = []
teams_list = []
teams_list = teams.get_teams()

@app.before_request
def add_user_to_g():
    """If user logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]



@app.route('/signup', methods=["GET", "POST"])
def signup():
    """user signup

    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", 'danger')
            return render_template('signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout')
def logout():
    """Handle logout of user."""

    do_logout()

    flash("User has logged out", 'success')
    return redirect("/login")

@app.route("/")
def root():
    """Homepage."""
    
    return render_template('home.html')




##player_dict = players.get_players()
###Use ternary operator or write function
###Names are case sensitive
##bron =[player for player in player_dict if player['full_name']=='LeBron James'][0]
##bron_id = bron['id']
##
##print (bron, bron_id)

##class Fpts:
##    def __init__(self, fpts):
##        self.fpts =fpts
##
##    def __repr__(self): 
##        return "Test fpts:% s" % (self.fpts) 
##
##    def __str__(self): 
##        return "From str method of Test: fpts is % s, " % (self.fpts) 
    

## bron_fpts = playerfantasyprofile.PlayerFantasyProfile(player_id='2544', season_type_playoffs='Regular Season')
## bron_df = bron_fpts.get_data_frames()[4]
## 
## print(bron_df.head(32))










