from flask import Flask, request, jsonify, render_template, session, flash, redirect, g
from nba_api.stats.library import parameters, data
from nba_api.stats.endpoints import playerfantasyprofile, commonplayerinfo
from models import db, User, Player, UserTeam
from forms import LoginForm, UserTeamPlayerAdd, PlayerSearchFrom
import pandas as pd
from IPython.display import HTML

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

headers = {
    "Connection": "keep-alive",
    "Accept": "application/json, text/plain, */*",
    "x-nba-stats-token": "true",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36",
    "x-nba-stats-origin": "stats",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-Mode": "cors",
    "Referer": "https://stats.nba.com/",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9",
}


class PlayerFantasy:
    def __init__(self, player_id):
        self.player_id = player_id
        self.common_data = None

    def get_player_stats_avg(self):
        """
        function to get a players avg stats in the current season
        """

        data1 = playerfantasyprofile.PlayerFantasyProfile(
            player_id=self.player_id,
            season_type_playoffs="Regular Season",
            per_mode36="PerGame",
            headers=headers,
        )

        df1 = data1.get_data_frames()[0]

        data2 = playerfantasyprofile.PlayerFantasyProfile(
            player_id=self.player_id,
            season_type_playoffs="Regular Season",
            per_mode36="PerGame",
            headers=headers,
            season="2020-21",
        )
        # add if statement for rookies. consider season as a changing value so its always prev season

        df2 = data2.get_data_frames()[0]

        df = df1.append(df2)

        stats_avg = df[stats_used]

        stats_avg.rename(
            columns={
                "GROUP_VALUE": "SEASON",
                "NBA_FANTASY_PTS": "FPTS",
                "FG_PCT": "FG%",
                "FG3_PCT": "FG3%",
                "FT_PCT": "FT%",
            },
            inplace=True,
        )

        stats_avg_new = stats_avg.head()

        html = stats_avg_new.to_html()
        return html

    def get_player_stats_total(self):
        """
        function to get a players total stats in the current season
        """
        data1 = playerfantasyprofile.PlayerFantasyProfile(
            player_id=self.player_id,
            season_type_playoffs="Regular Season",
            per_mode36="Totals",
        )

        df1 = data1.get_data_frames()[0]

        data2 = playerfantasyprofile.PlayerFantasyProfile(
            player_id=self.player_id,
            season_type_playoffs="Regular Season",
            per_mode36="Totals",
            season="2020-21",
        )

        df2 = data2.get_data_frames()[0]

        df = df1.append(df2)

        stats_tot = df[stats_used]

        stats_tot.rename(
            columns={
                "GROUP_VALUE": "SEASON",
                "NBA_FANTASY_PTS": "FPTS",
                "FG_PCT": "FG%",
                "FG3_PCT": "FG3%",
                "FT_PCT": "FT%",
            },
            inplace=True,
        )

        stats_tot_new = stats_tot.head()

        html = stats_tot_new.to_html()

        return html

    def get_lastngames_stats(self):
        """Function to request lastngames stats. SHould display last 5 and 10 games"""

        if not self.common_data:
            self.common_data = playerfantasyprofile.PlayerFantasyProfile(
                player_id=self.player_id, per_mode36="PerGame"
            ).get_data_frames()

        df = self.common_data[2]

        stats_n_games = df[stats_used]

        stats_n_games.rename(
            columns={
                "GROUP_VALUE": "N-GAMES",
                "NBA_FANTASY_PTS": "FPTS",
                "FG_PCT": "FG%",
                "FG3_PCT": "FG3%",
                "FT_PCT": "FT%",
            },
            inplace=True,
        )

        stats_n_games_new = stats_n_games.head()

        html = stats_n_games_new.to_html()

        return html

    def get_player_stats_opponents(self):
        """Function to get stats for a player vs an opponent"""
        if not self.common_data:
            self.common_data = playerfantasyprofile.PlayerFantasyProfile(
                player_id=self.player_id, per_mode36="PerGame"
            ).get_data_frames()

        df = self.common_data[4]

        stats_vs = df[stats_used]

        stats_vs.rename(
            columns={
                "GROUP_VALUE": "OPPONENT",
                "NBA_FANTASY_PTS": "FPTS",
                "FG_PCT": "FG%",
                "FG3_PCT": "FG3%",
                "FT_PCT": "FT%",
            },
            inplace=True,
        )

        stats_vs_new = stats_vs.head(32)

        html = stats_vs_new.to_html()

        return html

    def get_player_stats_location(self):
        """Function to return player stats per game for home vs away games"""
        if not self.common_data:

            self.common_data = playerfantasyprofile.PlayerFantasyProfile(
                player_id=self.player_id, per_mode36="PerGame"
            ).get_data_frames()

        df = self.common_data[1]

        stats_loc = df[stats_used]

        stats_loc.rename(
            columns={
                "GROUP_VALUE": "LOCATION",
                "NBA_FANTASY_PTS": "FPTS",
                "FG_PCT": "FG%",
                "FG3_PCT": "FG3%",
                "FT_PCT": "FT%",
            },
            inplace=True,
        )

        stats_loc_new = stats_loc.head()

        html = stats_loc_new.to_html()

        return html

    def get_position_and_team(self):
        """get updated position and team data for a specific player"""

        player_data = commonplayerinfo.CommonPlayerInfo(player_id=self.player_id)

        df = player_data.get_data_frames()[0]

        info_new = df[player_info_add]
        info_new.head()

        return info_new.head()
