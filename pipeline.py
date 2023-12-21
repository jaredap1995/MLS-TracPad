import gc
from extractAPIdata import ExtractAPIData

match_ids = 'get from physical_data'
games = list(game for game in match_ids)
var_names = 'whatever you would like to call your files'

def save_data_to_file(data, filename):
    with open(f"{filename}.txt", "w") as file:
        file.write(data)

def process_game_data(games, var_names):
    for gameID, var_name in zip(games, var_names):
        success = False
        while not success:
            data = ExtractAPIData(gameID).fetch_tactical_data()
            if data: 
                save_data_to_file(data, var_name)
                success = True
                gc.collect()

process_game_data(games, var_names)