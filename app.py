from flask import (
    Flask,
    request,
    render_template,
    session,
    flash,
    redirect,
    g,
    url_for,
)
from sqlalchemy.exc import IntegrityError
import pandas as pd
from IPython.display import HTML
from models import db, connect_db, User, Player, UserTeam,PlayerStats
from forms import (
    SignUpForm,
    LoginForm,
    UserTeamPlayerAdd,
    PlayerSearchFrom,
    UserEditForm,
)
from helper import PlayerFantasy
import os
import json

CURR_USER_KEY = "curr_user"

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "postgresql:///nba_stats")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = False
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = True
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "p-word-here-shhhhh")

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
    form.player_names.choices.insert(0, ('', ''))


    if request.method == "POST":

        player_id = form.data["player_names"]

        if player_id == '':

            flash("Enter Current NBA Player", "danger")
            return render_template("home.html", form=form)

        return redirect(url_for("player_page", player_id=player_id))

    return render_template("home.html", form=form)


@app.route("/stats/<int:player_id>")
def player_page(player_id):
    """Display player page. Call information from helper.py"""

    # getting player stats and info via helper.py
    player = Player.query.get_or_404(player_id)
    player_stats=PlayerStats.query.filter_by(player_id=player_id)
    if player_stats[0]:
        a = player_stats[0].position_team
        d = pd.DataFrame.from_dict(player_stats[0].player_stats_total).to_html(index=False).replace("dataframe", "stats")
        f = pd.DataFrame.from_dict(player_stats[0].player_stats_avg).to_html(index=False).replace("dataframe", "stats")
        h = pd.DataFrame.from_dict(player_stats[0].player_stats_location).to_html(index=False).replace("dataframe", "stats")
        g = pd.DataFrame.from_dict(player_stats[0].last_n_games_stats).to_html(index=False).replace("dataframe", "stats")
        s = pd.DataFrame.from_dict(player_stats[0].player_stats_opponents).to_html(index=False).replace("dataframe", "stats")

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

    if exp == 0:
        exp = 'R'
    else:
        None

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
        exp=exp,
    )


@app.route("/users/<int:user_id>/team/new", methods=["GET", "POST"])
def create_new_team(user_id):
    """Page to create a new fantasy team for specific user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")
    
    form = UserTeamPlayerAdd()
    query = db.session.query(Player.id, Player.full_name).all()
    form.player_name.choices = query
    form.player_name.choices.insert(0, ('', ''))

    if request.method == "POST":
        all_players = []
        user_players = UserTeam.query.filter_by(user_id=user_id).all()
        for player in user_players:
            if player.player_id not in request.json["players"].keys():
                UserTeam.query.filter_by(user_id=user_id, player_id=player.player_id).delete()
                db.session.commit()
        for pId in request.json["players"].keys():
            u = UserTeam.query.filter_by(player_id=pId, user_id=user_id).first()
            if not u:
                all_players.append(UserTeam(player_id=pId, user_id=user_id))
        db.session.bulk_save_objects(all_players)
        db.session.commit()
        
        return redirect("/")


    my_players = (
        UserTeam.query.filter_by(user_id=g.user.id).with_entities("player_id").all()
    )
    added_players = []
    for player in my_players:
        added_players.append(player[0])
    return render_template(
        "/users/createteam.html",
        form=form,
        addedPlayers=json.dumps(added_players),
    )



@app.route("/users/profile", methods=["GET", "POST"])
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
            g.user.image_url = (
                form.image_url.data or User.background_image.default.arg,
            )
            db.session.commit()

            return redirect("/home")

        flash("Incorrect password, please try again.", "danger")

    return render_template("users/edit.html", form=form, user_id=g.user.id)


@app.route("/users/delete", methods=["POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

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
    req.headers["Cache-Control"] = "public, max-age=0"
    return req


if __name__ == "__main__":
    app.run(debug=True)
