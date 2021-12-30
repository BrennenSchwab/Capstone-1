from flask import Flask, request, jsonify, render_template, session, flash, redirect
from nba_api.stats.library import data, parameters
from nba_api.stats.static import team, players
from nba_api.stats.endpoints import playerfantasyprofile
import pandas as pd
from models import db, connect_db

app = Flask(__name__)
connect_db(app)

@app.route("/")
def root():
    """Homepage."""

    return redirect("/home")

##app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///nba_stats'
##app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
##app.config['SECRET_KEY'] = "p-word-here-shhhhh
## add stats vs certain team for season to help with DFS. And projections

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










