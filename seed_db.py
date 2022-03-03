from nba_api.stats.endpoints import playerfantasyprofile, commonplayerinfo
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
    "BIRTHDATE",
    "SCHOOL",
    "COUNTRY",
    "HEIGHT",
    "WEIGHT",
    "SEASON_EXP",
    "POSITION",
    "TEAM_NAME",
    "TEAM_ABBREVIATION",
    "TEAM_CITY",
    
]

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
        )

        df1 = data1.get_data_frames()[0]

        data2 = playerfantasyprofile.PlayerFantasyProfile(
            player_id=self.player_id,
            season_type_playoffs="Regular Season",
            per_mode36="PerGame",
            season="2020-21",
        )

        df2 = data2.get_data_frames()[0]

        df = df1.append(df2)

        stats_avg = df[stats_used].copy()

        stats_avg_new = stats_avg.rename(
            columns={
                "GROUP_VALUE": "SEASON",
                "NBA_FANTASY_PTS": "FPTS",
                "FG_PCT": "FG%",
                "FG3_PCT": "FG3%",
                "FT_PCT": "FT%",
            }
        )
        for (columnName, columnData) in stats_avg_new.iteritems():
            for value in columnData:
                try:
                    value=float(value)
                except:
                    pass
        res=stats_avg_new.to_dict('records')
        
        return res

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
        
        stats_tot = df[stats_used].copy()

        stats_tot_new = stats_tot.rename(
            columns={
                "GROUP_VALUE": "SEASON",
                "NBA_FANTASY_PTS": "FPTS",
                "FG_PCT": "FG%",
                "FG3_PCT": "FG3%",
                "FT_PCT": "FT%",
            }
        ).round({'MIN': 1})

        for (columnName, columnData) in stats_tot_new.iteritems():
            for value in columnData:
                try:
                    value=float(value)
                except:
                    pass
        res=stats_tot_new.to_dict('records')

        return res

    def get_lastngames_stats(self):
        """Function to request lastngames stats. SHould display last 5 and 10 games"""

        if not self.common_data:
            self.common_data = playerfantasyprofile.PlayerFantasyProfile(
                player_id=self.player_id, per_mode36="PerGame"
            ).get_data_frames()

        df = self.common_data[2]

        stats_n_games = df[stats_used].copy()

        stats_n_games_new = stats_n_games.rename(
            columns={
                "GROUP_VALUE": "GAMES STREAK (avg)",
                "NBA_FANTASY_PTS": "FPTS",
                "FG_PCT": "FG%",
                "FG3_PCT": "FG3%",
                "FT_PCT": "FT%",
            }
        )
        for (columnName, columnData) in stats_n_games_new.iteritems():
            for value in columnData:
                try:
                    value=float(value)
                except:
                    pass
        res=stats_n_games_new.to_dict('records')
        return res

    def get_player_stats_opponents(self):
        """Function to get stats for a player vs an opponent"""
        if not self.common_data:
            self.common_data = playerfantasyprofile.PlayerFantasyProfile(
                player_id=self.player_id, per_mode36="PerGame"
            ).get_data_frames()

        df = self.common_data[4]

        stats_vs = df[stats_used].copy()

        stats_vs_new = stats_vs.rename(
            columns={
                "GROUP_VALUE": "OPPONENT",
                "NBA_FANTASY_PTS": "FPTS",
                "FG_PCT": "FG%",
                "FG3_PCT": "FG3%",
                "FT_PCT": "FT%",
            }
        ).head(32)
        for (columnName, columnData) in stats_vs_new.iteritems():
            for value in columnData:
                try:
                    value=float(value)
                except:
                    pass
        res=stats_vs_new.to_dict('records')
        return res

    def get_player_stats_location(self):
        """Function to return player stats per game for home vs away games"""
        if not self.common_data:

            self.common_data = playerfantasyprofile.PlayerFantasyProfile(
                player_id=self.player_id, per_mode36="PerGame"
            ).get_data_frames()

        df = self.common_data[1]

        stats_loc = df[stats_used].copy()

        stats_loc_new = stats_loc.rename(
            columns={
                "GROUP_VALUE": "LOCATION",
                "NBA_FANTASY_PTS": "FPTS",
                "FG_PCT": "FG%",
                "FG3_PCT": "FG3%",
                "FT_PCT": "FT%",
            }
        )
        for (columnName, columnData) in stats_loc_new.iteritems():
            for value in columnData:
                try:
                    value=float(value)
                except:
                    pass
        res=stats_loc_new.to_dict('records')
        return res

    def get_position_and_team(self):
        """get updated position and team data for a specific player"""

        player_data = commonplayerinfo.CommonPlayerInfo(player_id=self.player_id)

        df = player_data.get_data_frames()[0]

        info_new = df[player_info_add].copy()
        position = info_new.at[0, 'POSITION']
        abbr = info_new.at[0, 'TEAM_ABBREVIATION']
        team_name = info_new.at[0, 'TEAM_NAME']
        team_city = info_new.at[0, 'TEAM_CITY']
        school = info_new.at[0, 'SCHOOL']
        birthdate = info_new.at[0, 'BIRTHDATE'].split('T')[0]
        country = info_new.at[0, 'COUNTRY']
        height = info_new.at[0, 'HEIGHT']
        weight = float(info_new.at[0, 'WEIGHT'])
        exp = float(info_new.at[0, 'SEASON_EXP'])
    
        return [
            position, 
            abbr, 
            team_name, 
            team_city, 
            school, 
            birthdate, 
            country, 
            height, 
            weight, 
            exp]


