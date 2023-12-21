import pandas as pd
import json
import json



class TracPad:
    """
    TracPad is a class for analyzing tactical and physical data from soccer matches.

    Attributes:
        df: A DataFrame containing the tactical data.
        physical_data: A dictionary containing the physical data loaded from JSON.
        home_team_physical: DataFrame of home team's physical data.
        away_team_physical: DataFrame of away team's physical data.
        first_half_end: The frame count where the first half ends.
        second_half_start: The frame count where the second half starts.
        useless_frames: A list of frames that are not useful for analysis.
        index: The index of the DataFrame after removing useless frames.
    """

    def __init__(self, tactical_data_path, physical_data_path):
        """
        Initializes the TracPad object with tactical and physical data.

        Args:
            tactical_data_path: The file path to the tactical data CSV.
            physical_data_path: The file path to the physical data JSON.
        """
        self.df = pd.read_csv(tactical_data_path, sep=';', header=None)
        split_columns = self.df[0].str.split(':', expand=True)
        split_columns.rename({1: 'temporary', 0: 'FrameCount'}, axis=1, inplace=True)
        self.df = pd.concat([split_columns, self.df.iloc[:, 1:]], axis=1)
        self.ball_df = self.df[29]
        self.df.drop(columns=[29, 30], inplace=True)

        if type(physical_data_path) == str:
            with open(physical_data_path, 'r') as file:
                self.physical_data = json.load(file)
        else:
            self.physical_data = physical_data_path

        self.home_team_physical = pd.DataFrame(self.physical_data['HomeTeam']['Players'])
        self.away_team_physical = pd.DataFrame(self.physical_data['AwayTeam']['Players'])

        self.first_half_end = self.physical_data['Phase1EndFrame']
        self.second_half_start = self.physical_data['Phase2StartFrame']

        self.useless_frames = list(set(range(self.first_half_end, self.second_half_start)))

        self.df['FrameCount'] = self.df['FrameCount'].astype(int)
        self.df = self.df[~self.df['FrameCount'].isin(self.useless_frames)]
        self.index = self.df.index

        self.home_team_df = None
        self.away_team_df = None
        self.ball_data = None

    def player_helper(self, col):
        """Helper method to extract player data from a column."""
        col_names = ['TeamType', 'PlayerID', 'JerseyNumber', 'XPosition', 'YPosition', 'PlayerSpeed']
        expanded_cols = col.str.split(',', expand=True)
        expanded_cols.columns = col_names
        return expanded_cols[expanded_cols['TeamType'].isin(['0', '1'])]

    def ball_helper(self, col):
        """Helper method to extract ball data from a column."""
        col_names = ['BallPositionX', 'BallPositionY', 'BallPositionZ', 'BallSpeed', 'Possession', 'BallFlags']
        expanded_cols = col.str.split(',', expand=True).iloc[:, :6]
        expanded_cols.columns = col_names
        temp = expanded_cols['BallPositionX'].str.split(':', expand=True)
        expanded_cols['BallPositionX'] = temp[1]
        expanded_cols = expanded_cols[expanded_cols.index.isin(self.index)]
        return expanded_cols

    def get_team_data(self, team_type):
        """Retrieves tactical data for a specified team type ('0' for away, '1' for home)."""
        team_data = pd.DataFrame()
        team_data['FrameCount'] = self.df['FrameCount']
        for col in self.df.columns[1:]:
            player_data = self.player_helper(self.df[col])
            if player_data is not None and not player_data.empty:
                player_data = player_data[player_data['TeamType'] == team_type] 
                team_data = pd.concat([team_data, player_data.drop(columns=['TeamType', 'PlayerID'])], axis=1)
        return team_data

    def get_away_team(self):
        """Retrieves tactical data for the away team."""
        if self.away_team_df is None:
            self.away_team_df = self.get_team_data('0')
        return self.away_team_df

    def get_home_team(self):
        """Retrieves tactical data for the home team."""
        if self.home_team_df is None:
            self.home_team_df = self.get_team_data('1')
        return self.home_team_df

    def get_ball_data(self):
        """Retrieves ball data."""
        if self.ball_data is None:
            ball_data = self.ball_helper(self.ball_df)
            ball_data['FrameCount'] = self.df[self.df.columns[0]]
            reordered_cols = [ball_data.columns[-1]] + list(ball_data.columns[:-1])
            self.ball_data = ball_data[reordered_cols]
        return self.ball_data
    
    def ball_team(self, team_type):
        """Combines ball data with team data based on the specified team type."""
        team_type = team_type.lower()
        ball_data = self.get_ball_data()
        if team_type == 'home':
            home_team = self.get_home_team()
            home_team.drop(columns='FrameCount', inplace=True)
            ball_team = pd.concat([ball_data, home_team], axis=1)
        elif team_type == 'away':
            away_team = self.get_away_team()
            away_team.drop(columns='FrameCount', inplace=True)
            ball_team = pd.concat([ball_data, away_team], axis=1)
        else:
            raise ValueError('team_type must be either "home" or "away"')
        return ball_team
    
    def whole_field(self):
        """Combines ball data with both home and away team data."""
        home_team = self.get_home_team()
        away_team = self.get_away_team()
        ball_data = self.get_ball_data()
        home_team.drop(columns='FrameCount', inplace=True)
        away_team.drop(columns='FrameCount', inplace=True)
        return pd.concat([ball_data, home_team, away_team], axis=1)
    
    def isolate_player(self, jersey_number, team_type):
        """
        Isolates the data for a player with the specified jersey number from the tactical data.

        Meant to be called on a HOME or AWAY team DataFrame.

        Args:
            jersey_number: The jersey number of the player to isolate.

        Returns:
            A DataFrame with the isolated player data.
        """
        if team_type == 'home':
            if self.home_team_df is None:
                self.home_team_df = self.get_home_team()
            team_df = self.home_team_df
        elif team_type == 'away':
            if self.away_team_df is None:
                self.away_team_df = self.get_away_team()
            team_df = self.away_team_df
        else:
            raise ValueError('team_type must be either "home" or "away"')
        

        player_df = pd.DataFrame()
        frame_count = team_df['FrameCount']
        for i in range(len(team_df.columns)):
            if team_df.columns[i] == 'JerseyNumber':
                subset = team_df.iloc[:, i:i+4]
                subset['JerseyNumber'] = subset['JerseyNumber'].fillna(-1).astype(int)

                # Isolate Player
                subset = pd.concat([frame_count, subset], axis=1)
                subset = subset[subset['JerseyNumber'] == jersey_number]

                # Cast to integer
                subset['XPosition'] = subset['XPosition'].astype(float)
                subset['YPosition'] = subset['YPosition'].astype(float)
                subset['PlayerSpeed'] = subset['PlayerSpeed'].astype(float)

                # Drop JerseyNumber
                subset.drop(columns='JerseyNumber', inplace=True)
                player_df = pd.concat([player_df, subset], axis=0)

        player_df.sort_values(by='FrameCount', inplace=True)
        return player_df, team_df
