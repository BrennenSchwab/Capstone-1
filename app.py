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
from forms import SignUpForm, LoginForm, UserTeamPlayerAdd, PlayerSearchFrom
from helper import stats_used, PlayerFantasy


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
        return redirect(url_for("player_page", player_id=player_id))

    return render_template("home.html", form=form)


@app.route("/stats/<int:player_id>")
def player_page(player_id):
    """Display player page"""

    player = Player.query.get_or_404(player_id)
    player_fantasy = PlayerFantasy(player_id)
    a = player_fantasy.get_position_and_team()
    d = player_fantasy.get_player_stats_total()
    f = player_fantasy.get_player_stats_avg()
    h = player_fantasy.get_player_stats_location()
    g = player_fantasy.get_lastngames_stats()
    s = player_fantasy.get_player_stats_opponents()

    results = str(f)

    return render_template(
        "playerpage.html", player_id=player_id, results=results, player=player
    )


@app.errorhandler(404)
def page_not_found(e):
    """Show 404 NOT FOUND page."""

    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
