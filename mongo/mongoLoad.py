from mongo.mongoPreprocessing import MongoPreprocessing
import json

class MongoLoad:
    def __init__(self, client, db, collection, match_data_path, tracpad):
        # Extract the match_data
        self.client = client
        self.db = self.client[db]
        self.collection = collection

        # Read match_data from file
        with open(match_data_path, 'r') as file:
            self.physical = json.load(file) # Read match_data as JSON object

        ## TracPad Object ###
        self.tp = tracpad

        ###### Away then Home #####
        self.teams = [self.physical['AwayTeam']['LongName'].lower(),self.physical['HomeTeam']['LongName'].lower()]

        ########################################################################
        input_team = input(f'Please enter the team you would like to analyze. The options are \n \n Away Team: {self.teams[0]} \n or \n Home Team: {self.teams[1]} \n \n ')
        self.team = input_team.lower()
        ########################################################################

        if self.team in self.teams:
            idx = self.teams.index(self.team)
            self.side = 'away' if idx == 0 else 'home'
            self.team_physical = self.tp.away_team_physical if idx == 0 else self.tp.home_team_physical

    def tactical_ball_load(self):

        """ Let's initialize some checks to see if there is a response within the collection that matches the gameID so we can warn the user that they may be duplicating data"""

        collection = self.collection #Typically used "TracPad or TracPad_Ball etc."
        ball_data = self.tp.get_ball_data()


        processed_ball_data = MongoPreprocessing(player_df=None, ball_df=ball_data).process_ball(self.physical)
        db_data = processed_ball_data.to_dict(orient = 'records')
        try:
            collection.insert_many(db_data)
            print("Successfully Uploaded Ball Data For GameID", self.physical['GameID'])
        except Exception as e:
            print('Failed to Upload Ball Data for Game ', self.physical['GameID'], e)



    def tactical_player_load(self): #Loads every Player who played that game
        collection = self.collection #Typically used "TracPad or TracPad_Ball etc."

        """ Let's initialize some checks to see if there is a response within the collection that matches the gameID so we can warn the user that they may be duplicating data"""

        for playerNo in self.team_physical['JerseyNo'].to_list():
            #Skip players who did not play
            if self.team_physical[self.team_physical['JerseyNo'] == playerNo]['StartFrameCount'].iloc[0] == 0: continue

            player_data, _ = self.tp.isolate_player(playerNo, self.side)

            ######## Can add line here to save player data to CSV for Tableau Analysis######

            preprocessed_player_data = MongoPreprocessing(player_df=player_data).process_player(playerNo, self.physical, self.team_physical)
            db_data = preprocessed_player_data.to_dict(orient = 'records')
            try:
                self.db[collection].insert_many(db_data)
                print("Successfully uploaded Player Data for Player Number ", playerNo, "in Game", self.physical['GameID'])
            except Exception as e:
                print('failed to upload: ', e)
                break

    def insert_metadata(self):
        data = self.physical
        if data is not None:
            action = input('Would you like to upload this data into Mongo? Type "Yes" or "No"').lower()

            if action == 'yes':
                try:
                    data['_id'] = data.pop('GameID')
                    self.collection.insert_one(data)
                    print('Successfully uploaded data into Mongo')
                except Exception as e:
                    print('Error', e)
            else:
                print('Data was not uploaded into Mongo')
