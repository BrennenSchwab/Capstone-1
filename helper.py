from flask import Flask, request, jsonify, render_template, session, flash, redirect, g
from nba_api.stats.library import parameters, data
from nba_api.stats.endpoints import playerfantasyprofile, commonplayerinfo
from models import db, User, Player, UserTeam
from forms import LoginForm, UserTeamPlayerAdd, PlayerSearchFrom
import pandas as pd

stats_used = [
    "GROUP_VALUE",
    "GP",
    "W",
    "L",
    "MIN",
    "FGM",
    "FGA",
    "FG_PCT",
    "FG3M",
    "FG3A",
    "FG3_PCT",
    "FTM",
    "FTA",
    "FT_PCT",
    "OREB",
    "DREB",
    "REB",
    "AST",
    "TOV",
    "STL",
    "BLK",
    "PF",
    "PTS",
    "NBA_FANTASY_PTS",
]


player_info_add = [
    "POSITION",
    "TEAM_ABBREVIATION",
]


def get_player_stats_avg(player_id):
    """
    function to get a players avg stats in the current season
    """
    data1 = playerfantasyprofile.PlayerFantasyProfile(
        player_id=player_id, season_type_playoffs="Regular Season", per_mode36="PerGame"
    )

    df = data1.get_data_frames()[0]
    stats_avg1 = df[stats_used]

    data2 = playerfantasyprofile.PlayerFantasyProfile(
        player_id=player_id, season_type_playoffs="Regular Season", per_mode36="PerGame", season='2020-21'
    )
    # add if statement for rookies. consider season as a changing value so its always prev season
    df = data2.get_data_frames()[0]
    stats_avg2 = df[stats_used]

    return (stats_avg1.head(), stats_avg2.head())


def get_player_stats_total(player_id):
    """
    function to get a players total stats in the current season
    """
    data1 = playerfantasyprofile.PlayerFantasyProfile(
        player_id=player_id, season_type_playoffs="Regular Season", per_mode36="Totals"
    )

    df = data1.get_data_frames()[0]

    stats_totals1 = df[stats_used]

    data2 = playerfantasyprofile.PlayerFantasyProfile(
        player_id=player_id, season_type_playoffs="Regular Season", per_mode36="Totals", season='2020-21'
    )

    df = data2.get_data_frames()[0]

    stats_totals2 = df[stats_used]

    return (stats_totals1.head(), stats_totals2.head())


def get_lastngames_stats(player_id):
    """Function to request lastngames stats. SHould display last 5 and 10 games"""

    data = playerfantasyprofile.PlayerFantasyProfile(
        player_id=player_id, per_mode36="PerGame"
    )

    df = data.get_data_frames()[2]

    stats_n_games = df[stats_used]

    return stats_n_games.head()


def get_player_stats_opponents(player_id):
    """Function to get stats for a player vs an opponent"""

    data = playerfantasyprofile.PlayerFantasyProfile(
        player_id=player_id, per_mode36="PerGame"
    )

    df = data.get_data_frames()[4]

    stats_vs = df[stats_used]

    return stats_vs.head(32)


def get_player_stats_location(player_id):
    """Function to return player stats per game for home vs away games"""

    data = playerfantasyprofile.PlayerFantasyProfile(
        player_id=player_id, per_mode36="PerGame"
    )

    df = data.get_data_frames()[1]

    stats_loc = df[stats_used]

    return stats_loc.head()


def get_position_and_team(player_id):
    """get updated position and team data for a specific player"""

    player_data = commonplayerinfo.CommonPlayerInfo(player_id=player_id)

    df = player_data.get_data_frames()[0]

    info_new = df[player_info_add]

    return info_new.head()
