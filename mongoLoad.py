from mongoPreprocessing import MongoPreprocessing
from pymongo import MongoClient

class MongoLoad:
    def __init__(self, match_data, tracpad):

        #Extract the match_data
        self.client = MongoClient('mongodb://your_host_path')
        self.db = self.client['your_db_name']
        self.physical = match_data #needs to be JSON Object that is provided by MLS API

        ## TracPad Object ###
        self.tp = tracpad

        ###### Away then Home #####
        self.teams = [self.physical['AwayTeam']['LongName'].lower(),self.physical['HomeTeam']['LongName'].lower()]

        ########################################################################
        ### Must Replace with name of team interested in examining #####
        self.team = "team_of_interest".lower()
        ########################################################################

        if self.team in self.teams:
            idx = self.teams.index(self.team)
            self.side = 'away' if idx == 0 else 'home'
            self.team_physical = self.tp.away_team_physical if idx == 0 else self.tp.home_team_physical

    def ball_load(self):
        collection = self.db['collection_name'] #Typically used "TracPad or TracPad_Ball etc."
        ball_data = self.tp.get_ball_data()


        processed_ball_data = MongoPreprocessing(player_df=None, ball_df=ball_data).process_ball(self.physical)
        db_data = processed_ball_data.to_dict(orient = 'records')
        try:
            collection.insert_many(db_data)
            print("Successfully Uploaded Ball Data For GameID", self.physical['_id'])
        except Exception as e:
            print('Failed to Upload Ball Data for Game ', self.physical['_id'], e)



    def tactical_player_load(self): #Loads every Player who played that game
        collection = self.db['TracPad']

        for playerNo in self.team_physical['JerseyNo'].to_list():
            #Skip players who did not play
            if self.team_physical[self.team_physical['JerseyNo'] == playerNo]['StartFrameCount'].iloc[0] == 0: continue

            player_data, _ = self.tp.isolate_player(playerNo, self.side)

            ######## Can add line here to save player data to CSV for Tableau Analysis######

            preprocessed_player_data = MongoPreprocessing(player_df=player_data).process_player(playerNo, self.physical, self.team_physical)
            db_data = preprocessed_player_data.to_dict(orient = 'records')
            try:
                collection.insert_many(db_data)
                print("Successfully uploaded Player Data for Player Number ", playerNo, "in Game", self.physical['_id'])
            except Exception as e:
                print('failed to upload: ', preprocessed_player_data, e)
                break