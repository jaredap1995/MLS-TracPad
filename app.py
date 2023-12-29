from api.DataExtractor import DataProcessor
from tracPad import TracPad
import json

def load_config():
    with open('./config.json', 'r') as file:
        return json.load(file)
    
def extract_data(config):
    extractor = DataProcessor(config['GameID'], config['client'], config['db'], config['collection'], config['authorization_token'], config['VendorID'], config['ExtractionVersion'], config['dataQuality'], config['meta_endpoint'], config['tac_endpoint'])

    print(f'The Data Extractor is ready with the following parameters: {config}\n')

    choice = input("What would you like to do now? The options are 'meta', 'tac', or leave blank for both: ").lower()

    if choice == 'meta':
        extractor.process_game_data('meta')
    elif choice == 'tac':
        extractor.process_game_data('tac')
    else:
        extractor.process_game_data('both')

def transform_data():
    tactical_path = input('In order to process the data, please copy the filepath to the raw tactical data: ')
    physical_path = input('Now, please provide the filepath to the corresponding metadata for that game: ')
    tp = TracPad(tactical_data_path=tactical_path, physical_data_path=physical_path)
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
    # Will use MongoLoad stuff...TBD
    pass


def main():
    while True:
        config = load_config()
        if config:
            print(f"Your configuration file was properly read. Your current team of interest is: {config['team']}\n")
            print("If this is correct, then the values were properly loaded.")

        action = input("What action would you like to do today? Type 'Extract', 'Process' or 'Exit' to end the program: ").lower()

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
        elif action == 'exit':
            print("Exiting program.")
            break  # exit option
        else:
            print("Invalid action. Please type 'Extract', 'Process', or 'Exit'.")
            continue  # Restarts the loop for any other invalid inputs

if __name__ == "__main__":
    main()
