from socket import timeout
from turtle import position
from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    session,
    flash,
    redirect,
    g,
    url_for,
)
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql.elements import Null
from nba_api.stats.library import data, parameters
from nba_api.stats.static import teams, players
import pandas as pd
from IPython.display import HTML
from models import db, connect_db, User, Player, UserTeam
from forms import SignUpForm, LoginForm, UserTeamPlayerAdd, PlayerSearchFrom, UserEditForm
from helper import PlayerFantasy


CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///nba_stats"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = True
app.config["SECRET_KEY"] = "p-word-here-shhhhh"

connect_db(app)


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


@app.route("/signup", methods=["GET", "POST"])
def signup():
    """user signup"""

    form = SignUpForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
                background_image=form.background_image.data or User.background_image.default.arg,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username already taken", "danger")
            return render_template("signup.html", form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template("signup.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            do_login(user)
            return redirect("/")

        flash("Invalid credentials.", "danger")

    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    """Handle logout of user."""

    do_logout()

    flash("User has logged out", "success")
    return redirect("/login")


@app.route("/")
def root():
    return redirect("/home")


@app.route("/home", methods=["GET", "POST"])
def home():
    """Homepage and player search handling."""

    form = PlayerSearchFrom()

    query = db.session.query(Player.id, Player.full_name).all()
    form.player_names.choices = query

    if request.method == "POST":

        player_id = form.data["player_names"]
        
        if player_id == 'None':

            flash("Enter Current NBA Player", 'danger')
            return render_template('home.html', form=form)
        
        return redirect(url_for("player_page", player_id=player_id))
            
    return render_template("home.html", form=form)


@app.route("/stats/<int:player_id>")
def player_page(player_id):
    """Display player page. Call information from helper.py"""

    # getting player stats and info via helper.py
    player = Player.query.get_or_404(player_id)
    player_fantasy = PlayerFantasy(player_id)
    a = player_fantasy.get_position_and_team()
    d = player_fantasy.get_player_stats_total()
    f = player_fantasy.get_player_stats_avg()
    h = player_fantasy.get_player_stats_location()
    g = player_fantasy.get_lastngames_stats()
    s = player_fantasy.get_player_stats_opponents()

    # Turning htmls from helper functions into HTML tables
    avg_table = HTML(f)
    tot_table = HTML(d)
    ngames_table = HTML(g)
    loc_table = HTML(h)
    opp_table = HTML(s)

    # calling on common player info for each index value that is returned
    position = a[0]
    team_abbr = a[1]
    team_name = a[2]
    team_city = a[3]
    school = a[4]
    birthdate = a[5]
    country = a[6]
    height = a[7]
    weight = a[8]
    exp = a[9]

    team = str(team_city) + " " + str(team_name)


    return render_template(
        "playerpage.html", 
        avg=avg_table,
        total=tot_table,
        ngames=ngames_table,
        location=loc_table,
        opponent=opp_table,
        player=player,
        position=position,
        abbr=team_abbr,
        team=team,
        school=school,
        birthdate=birthdate,
        country=country,
        height=height,
        weight=weight,
        exp=exp
    )


@app.route('/users/team/new', methods=["GET", "POST"])
def create_new_team():
    """Page to create a new fantasy team for specific user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = UserTeamPlayerAdd()
    query = db.session.query(Player.id, Player.full_name).all()
    form.player_names.choices = query

    if request.method == "POST":

        players_added = UserTeam(player_id=form.data["player_names"])
        g.user.users_team.append(players_added)
        db.session.commit()

        return redirect(f"/users/team/{ g.user.users_teams.id }")

    return render_template('/users/team/new.html', form=form)


@app.route('/users/team/<int:users_team_id>')
def show_user_team(users_team_id):
    """Display a user's created team"""

    users_team = UserTeam.query.get_or_404(users_team_id)

    user = users_team.user_id
    players = users_team.player_id.get.all()#user.player_id
    
    for player in players:

        player_fantasy = PlayerFantasy(player)
        a = player_fantasy.get_position_and_team()
        f = player_fantasy.get_player_stats_avg()
        avg_table = HTML(f)
        position = a[0]
        team_abbr = a[1]

    return render_template("fantasyteams.html", users_team=users_team, user=user, avg=avg_table, position=position, abbr=team_abbr)


@app.route('/users/profile', methods=["GET", "POST"])
def profile():
    """Update profile for current user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = UserEditForm(obj=g.user)

    if form.validate_on_submit():
        if User.authenticate(g.user.username, form.password.data):
            g.user.username = form.username.data
            g.user.email = form.email.data
            g.user.image_url = form.image_url.data or User.background_image.default.arg,
            g.user.background_image = form.background_image.data or User.background_image.default.arg,

            db.session.commit()

            return redirect("/home")

        flash("Incorrect password, please try again.", 'danger')

    return render_template('users/edit.html', form=form, user_id=g.user.id)

@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = UserEditForm(obj=g.user)

    if form.validate_on_submit():
        if User.authenticate(g.user.username, form.password.data):   
            do_logout()
            db.session.delete(g.user)
            db.session.commit()
            return redirect("/")

@app.errorhandler(404)
def page_not_found(e):
    """Show 404 NOT FOUND page."""

    return render_template("404.html"), 404

@app.after_request
def add_header(req):
    """Add non-caching headers on every request."""

    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req

if __name__ == "__main__":
    app.run(debug=True)
