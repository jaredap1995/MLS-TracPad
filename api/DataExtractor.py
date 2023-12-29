import gc
from api.extractAPIdata import ExtractAPIData


class DataProcessor:
    def __init__(self, match_ids, client, db, collection, header, vendorID, ExtractionVersion, dataQuality, meta_endpoint, tac_endpoint):
        self.match_ids = match_ids
        self.var_names = [f"{match_id}_file" for match_id in match_ids]
        self.client = client
        self.db = db
        self.collection = collection
        self.header = header
        self.vendorID = vendorID
        self.ExtractionVersion = ExtractionVersion
        self.dataQuality = dataQuality
        self.meta_endpoint = meta_endpoint
        self.tac_endpoint = tac_endpoint

    def save_data_to_file(self, data, filename):
        with open(f"{filename}.txt", "w") as file:
            file.write(data)

    def process_game_data(self, choice):
        # Confirm the user's intent to process data
        match_ids = self.match_ids if isinstance(self.match_ids, list) else [self.match_ids]
        print(f"You have selected to process data for the following games: {match_ids}")
        user_confirm = input("Do you want to proceed? (yes/no): ").lower()
        if user_confirm != 'yes':
            print("Data processing cancelled.")
            return

        for gameID in match_ids:
            # Probably not the best approach to create an instance of ExtractAPIData for each gameID but anyway
            exAPI = ExtractAPIData(gameID, self.client, self.db, self.collection, self.header, self.vendorID, self.ExtractionVersion, self.dataQuality, self.meta_endpoint, self.tac_endpoint)

            if choice in ['meta', 'both']:
                metadata = exAPI.fetch_metadata()
                if metadata:
                    self.save_data_to_file(metadata, f"{gameID}_metadata")
                    gc.collect()

            if choice in ['tac', 'both']:
                success = False
                while not success:
                    data = exAPI.fetch_tactical_data()
                    if data:
                        self.save_data_to_file(data, gameID)
                        success = True
                        gc.collect()