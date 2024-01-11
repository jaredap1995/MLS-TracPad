from datetime import datetime, timedelta
import pandas as pd
import numpy as np

class MongoPreprocessing:
    def __init__(self, player_df=None, ball_df=None):
        self.player_df = player_df
        self.ball_df = ball_df

    def add_datetime_column(self, df, frame_counts, kickoff_time, frame_rate):
        """
        Adds a datetime column to a DataFrame based on the FrameCount and kickoff time.

        Args:
            df: DataFrame to which the datetime column will be added.
            frame_counts: List of frame counts.
            kickoff_time: Kickoff time string.
            frame_rate: Frame rate of the data.

        Returns:
            Modified DataFrame with an additional 'DT' column.
        """
        kickoff_datetime = datetime.strptime(kickoff_time, "%Y-%m-%d %H:%M:%S")

        def calculate_frame_datetime(frame_count):
            time_since_kickoff = timedelta(seconds=(frame_count - frame_counts[0]) / frame_rate)
            return kickoff_datetime + time_since_kickoff

        df['DT'] = [calculate_frame_datetime(frame) for frame in frame_counts]
        df['DT'] = pd.to_datetime(df['DT'])
        df.drop(columns=['FrameCount'], inplace=True)
        return df

    def process_ball(self, physical_json):
        """
        Processes ball tracking data.

        Args:
            physical_json: Dictionary containing match metadata.

        Returns:
            Modified self.ball_df DataFrame.
        """
        if self.ball_df is not None:
            frame_counts = self.ball_df['FrameCount'].tolist()
            self.ball_df['GameID'] = physical_json['_id']
            self.ball_df = self.add_datetime_column(
                self.ball_df, frame_counts, physical_json['Kickoff'], physical_json['FrameRate']
            )
            return self.ball_df

    def process_player(self, jersey_no, physical_json, team_data):
        """
        Processes tracking data for a soccer player.

        Args:
            jersey_no: The player's jersey number.
            physical_json: Dictionary containing match metadata.
            team_data: DataFrame containing team and player data.

        Returns:
            Modified self.player_df DataFrame.
        """
        if self.player_df is not None:
            # Calculate movement distances
            self.player_df['dist_x'] = np.diff(self.player_df['XPosition'], prepend=np.nan)
            self.player_df['dist_y'] = np.diff(self.player_df['YPosition'], prepend=np.nan)
            self.player_df['dist_cm'] = np.hypot(self.player_df['dist_x'], self.player_df['dist_y'])
            self.player_df['dist_m'] = self.player_df['dist_cm'] / 100

            # Assign PlayerID and GameID
            self.player_df['PlayerID'] = float(team_data['PlayerID'][team_data['JerseyNo'] == jersey_no].iloc[0])
            self.player_df['GameID'] = physical_json['GameID']

            # Add datetime column
            frame_counts = self.player_df['FrameCount'].tolist()
            self.player_df = self.add_datetime_column(
                self.player_df, frame_counts, physical_json['Kickoff'], physical_json['FrameRate']
            )
            return self.player_df
