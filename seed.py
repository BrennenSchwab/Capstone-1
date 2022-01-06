from nba_api.stats.library import parameters, data
from nba_api.stats.static import teams, players
from models import Player, Team
from app import db

db.drop_all()
db.create_all()

def seed_basic_player_info():
    """ Get general info for a player and store it"""
    players_list = []

    players_list = players.get_active_players()

    player_info = Player(
        id = players_list['id'],
        first_name = players_list['first_name'],
        last_name = players_list['last_name'],
        full_name = players_list['full_name'],
    )

    db.session.add(player_info)
    db.session.commit()
