from flask import Flask, request, jsonify, render_template, session, flash, redirect, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.elements import Null
from nba_api.stats.library import data, parameters
from nba_api.stats.static import teams, players
import pandas as pd
from models import db, connect_db, User, Player, Season, Team, UserTeam
from forms import SignUpForm, LoginForm, UserTeamPlayerAdd, PlayerSearchFrom
from helper import get_player_stats_opponents, get_player_stats_total, get_player_stats_avg, get_lastngames_stats, get_player_stats_location, get_position_and_team
from seed import seed_basic_player_info

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///nba_stats'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = "p-word-here-shhhhh"

connect_db(app)

seed_basic_player_info()

player_headshot = "https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/" + players_list['id'] + ".png"


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

    form = SignUpForm()

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

@app.route('/')
def root():
    return redirect('/home')

@app.route("/home")
def home():
    """Homepage."""
    
    form = PlayerSearchFrom()
    form.player_names.choices = [
        (player.id, player.full_name, player.last_name, player.first_name)
        for player in Player.query.order_by(Player.last_name, Player.first_name).all()]

    return render_template('home.html', form=form)

@app.route("/home", methods=["POST"])
def search_player():
    """ Search Player form handling"""
    search = request.args.get('q')

    if not search:
        flash("Entry not valid, Select a Current NBA Player")
        return redirect("/home")
    else:
        player = Player.query.filter(Player.full_name.like(f"%{search}%")).all()
        get_position_and_team(player_id=player.id)
        return redirect("/players")

@app.route("/players")
def players_search_results():

    return render_template("index.html") 


@app.route("players/<int:player_id>")
def player_page(player_id):
    """Display player page"""
    



@app.errorhandler(404)
def page_not_found(e):
    """Show 404 NOT FOUND page."""

    return render_template('404.html'), 404


if __name__ == "__main__":
    app.run(debug=True)









