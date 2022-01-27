from nba_api.stats.static import players
from models import Player
from app import db


db.drop_all()
db.create_all()

img_url = (
    "https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/"
)


def seed_basic_player_info():
    """Get general info for a player and store it"""
    players_list = []

    players_list = players.get_active_players()
    
    all_players = []
    for player in players_list:

        all_players.append(
            Player(
                id=player["id"],
                first_name=player["first_name"],
                last_name=player["last_name"],
                full_name=player["full_name"],
                player_img=img_url + str(player["id"]) + ".png",
            )
        )

    db.session.bulk_save_objects(all_players)
    db.session.commit()



seed_basic_player_info()
