from api.DataExtractor import DataProcessor
from tracPad import TracPad
from mongo.mongoLoad import MongoLoad
import json
from pymongo import MongoClient
import os

def load_config():
    with open('./config.json', 'r') as file:
        return json.load(file)
    
def extract_data(config):
    extractor = DataProcessor(config['GameID'], config['client'], config['db'], config['collection'], config['authorization_token'], config['VendorID'], config['ExtractionVersion'], config['DataQuality'], config['meta_endpoint'], config['tac_endpoint'])

    print(f'The Data Extractor is ready with the following parameters: {config}\n')

    choice = input("What would you like to do now? The options are 'meta', 'tac', or leave blank for both: ").lower()

    if choice == 'meta':
        extractor.process_game_data('meta')
    elif choice == 'tac':
        extractor.process_game_data('tac')
    else:
        extractor.process_game_data('both')

def transform_data():

    ##### Need to clean up this function for returning the dataframe data and turning it into CSV ######

    tactical_path = input('In order to process the data, please copy the filepath to the raw tactical data: ')
    physical_path = input('Now, please provide the filepath to the corresponding metadata for that game: ')
    tp = TracPad(tactical_data_path=tactical_path, physical_data_path=physical_path)

    ## Home team is always first in the list
    teams = (tp.physical_data['HomeTeam']['LongName'].lower(), tp.physical_data['AwayTeam']['LongName'].lower())
    side = input(f'Please enter the team you would like to analyze. The options are {teams[0]} or {teams[1]}: ').lower()

    next_action = input("""\n The TracPad object is ready. \n
          Current options are: 'player' for metrics like "total distance traveled, top speed, avg speed, etc", 'ball' elements like "possession split, etc., or 'team' to get the whole team's movement data (will contain NaN value)\n
            To get player data, type "player" or to get ball data, type "ball" or to exit, type "exit": \n
          """).lower()
    
    if next_action == 'player':
        player_no = input("Please enter the player number you would like to examine: ")
        try:
            player_no = int(player_no)
            player_data, _ = tp.isolate_player(player_no, 'home' if side == teams[0] else 'away')
            print(player_data)
            print("The player data has been printed to the console. Please check the console for the data.")
        except ValueError:
            print("Invalid player number. Please enter a valid number.")

    elif next_action == 'team':
        if side == teams[0]:  # Home team
            team_data = tp.get_home_team()
        else:  # Away team
            team_data = tp.get_away_team()
        
        print(team_data)
        print("The ball team data has been printed to the console. Please check the console for the data.")

    elif next_action == 'ball':
        ball_data = tp.get_ball_data()
        print(ball_data)
        print("The ball data has been printed to the console. Please check the console for the data.")

    elif next_action == 'exit':
        print("Exiting the data transformation process.")
        return
    else:
        print("Invalid input. Please enter 'player', 'team', 'ball', or 'exit'.")


def load_data(config):
    client = MongoClient(config['client'])
    while True:
        next_ = input(f'The currently configured database and collection are \n\n Database: {config["db"]} \n Colletion: {config["collection"]} \n\n Press y if correct [y]/n: ')
        if next_ == 'y' or not next_:
            break
        elif next_== 'n':
            new_db = input('Please enter the name of the database you would like to load into (if the database is correct and you would like to change the collection, leave blank): ')
            if new_db:
                try:
                    if new_db in client.list_database_names():
                        config['db'] = new_db
                        print(f'Your database has been changed to {config["db"]}')
                    else:
                        print('The database you entered does not exist. Please try a different database or create the databvase in Mongo.')
                except Exception as e:
                    print(e)
                    print('There was an error. Please try again.')
                    return
            new_collection = input('Please enter the name of the collection you would like to load into: ')
            if new_collection:
                try:
                    if new_collection in client[config['db']].list_collection_names():
                        config['collection'] = new_collection
                        print(f'Your collection has been changed to {config["collection"]}')
                    else:
                        new = input(f'The collection you entered does not exist. Would you like to create a new collection called {new_collection}? [y]/n: ')
                        if new == 'y' or not new:
                            client[config['db']][new_collection].insert_one({"created": "created"})
                            config['collection'] = new_collection
                            print('A new collection was created and added to your database.')
                except Exception as e:
                    print(e)
                    print('There was an error. Please try again.')
                    return
        else:
            print('Invalid input. Please enter y or n.')
            continue
    
    ## We need an input to tell the user the TP object is being loaded and check what the game IDS are, confirm then, and then check that the data exists within the correpsodnign directories
    tp_input = input('The current game IDS of interest are: \n\n' + str(config['GameID']) + '\n\n Please confirm that these are the correct game IDS. If not, please update the config.json file and restart the program. \n\n Press y if correct [y]/n: ')
    if tp_input == 'y' or not tp_input:
        meta_data_paths = []
        game_data_paths = []

        for game_id in config['GameID']:
            meta_path = os.path.join('metadata', f'{game_id}_metadata.json')
            game_path = os.path.join('gamedata', f'{game_id}.txt')

            if os.path.exists(meta_path):
                meta_data_paths.append(meta_path)
            if os.path.exists(game_path):
                game_data_paths.append(game_path)

    # For each game I need to load a TP object, so check if gameID of interest is a single game or multiple games
    # If single game, then load the TP object and then load the data into Mongo
    # If multiple, warn user and then start loop of actions, and at the end of the loading process for each game, tell the user what game theuy are moving on to next
    
    if len(config['GameID']) == 1:
        tp = TracPad(tactical_data_path=game_data_paths[0], physical_data_path=meta_data_paths[0])
        load_object = MongoLoad(client, config['db'], config['collection'], match_data_path=meta_data_paths[0], tracpad=tp)

        if load_object:
            choice = input("""The MongoLoad Object has been created successfully. Please select the data you would like to load into Mongo. 
                            The options are: \n\n 1. Player Data \n 2. Ball Data \n 3. Metadata \n\n 
                            Please enter the number corresponding to your choice. If left blank all 3 will be loaded: """)
            if choice == '1':
                print('Loading Player Data, this may take a couple minutes.')
                print('We are loading the data for every player who played in game ', config['GameID'][0], ' on team' , load_object.team, ' into the collection ', config['collection'], 'in the database ', config['db'])
                confirm = input('Please confirm that this is correct. Press y if correct [y]/n: ')
                if confirm == 'y' or not confirm:
                    load_object.tactical_player_load()
            elif choice == '2':
                # col_change = input('Would have chosen ball_data, would you like to change your collection to a ball specific collection or continue with ', config['collection'], 'continue = y, change = n. [y]/n')
                # if col_change == 'y':
                    ### Enter the new ncollection code ###
                    # pass
                # else:
                print('Loading Ball Data. \n We are loading the ball data for game ', config['GameID'][0], ' on team' , load_object.team, ' into the collection ', config['collection'], 'in the database ', config['db'])
                confirm = input('Please confirm that this is correct. Press y if correct [y]/n: ')
                if confirm == 'y' or not confirm:
                    load_object.tactical_ball_load()
                else:
                    print('Loading cancelled.')



def main():
    while True:
        config = load_config()
        if config:
            print(f"Your configuration file was properly read. Your gameID(s) of interest are: {config['GameID']}\n")
            print("If this is correct, then the values were properly loaded.")

        action = input("What action would you like to do today? Type 'Extract', 'Load', 'Process' or 'Exit' to end the program: ").lower()

        if action == 'extract':
            extract_data(config)
        elif action == 'process':
            decision = input("Have you already extracted the data? If not, please select 'no' and do so now. The TracPad class is currently constructed to work only with locally saved files. Type 'y' for Yes or 'n' for No: ").lower()
            if decision == 'y':
                transform_data(config)
            elif decision == 'n':
                print("Please extract the data first.")
                continue  # restarts from beginning
            else:
                print("Invalid input. Please enter 'y' or 'n'.")
                continue  # invalid input check
        elif action == 'load':
            load_data(config)
        elif action == 'exit':
            print("Exiting program.")
            break  # exit option
        else:
            print("Invalid action. Please type 'Extract', 'Process', 'Load', or 'Exit'.")
            continue  # Restarts the loop for any other invalid inputs

if __name__ == "__main__":
    main()
