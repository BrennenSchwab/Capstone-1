from nba_api.stats.static import players
from models import Player,PlayerStats
from app import db
from seed_db import PlayerFantasy
import time
db.drop_all()
db.create_all()

img_url = (
    "https://ak-static.cms.nba.com/wp-content/uploads/headshots/nba/latest/260x190/"
)


def seed_basic_player_info():
    """Get general info for a player and store it"""
    players_list = players.get_active_players()
    all_players = []
    stats=[]
    try:
        for idx,player in enumerate(players_list):
            print(str(idx+1) + " of " + str(len(players_list)))
            print(player)

            player_exists=Player.query.filter_by(id=player["id"])
            if not player_exists.count():
                all_players.append(
                    Player(
                        id=player["id"],
                        first_name=player["first_name"],
                        last_name=player["last_name"],
                        full_name=player["full_name"],
                        player_img=img_url + str(player["id"]) + ".png",
                    )
                )
            player_fantasy = PlayerFantasy(player["id"])
            player_stats_total=player_fantasy.get_player_stats_total() or {}

            position_team = player_fantasy.get_position_and_team() or {}

            player_stats_avg = player_fantasy.get_player_stats_avg() or {}
            #time.sleep(3)

            player_stats_location = player_fantasy.get_player_stats_location() or {}
            
            last_n_games_stats = player_fantasy.get_lastngames_stats() or {}
            
            player_stats_opponents = player_fantasy.get_player_stats_opponents() or {}
            player_stats_exist=PlayerStats.query.filter_by(player_id=player["id"])
            if player_stats_exist.count():
                player_stats=player_stats_exist[0]
                player_stats.player_stats_total=player_stats_total
                player_stats.position_team=position_team
                player_stats.player_stats_avg=player_stats_avg
                player_stats.player_stats_location=player_stats_location
                player_stats.last_n_games_stats=last_n_games_stats
                player_stats.player_stats_opponents=player_stats_opponents
                stats.append(player_stats)
            else:
                stats.append(PlayerStats(
                    player_id=player["id"],
                    player_stats_total=player_stats_total,
                    position_team=position_team,
                    player_stats_avg=player_stats_avg,
                    player_stats_location=player_stats_location,
                    last_n_games_stats=last_n_games_stats,
                    player_stats_opponents=player_stats_opponents
                ))
    except:
        print("FAILED")
        pass
    db.session.bulk_save_objects(all_players)
    db.session.bulk_save_objects(stats)
    db.session.commit()



seed_basic_player_info()
