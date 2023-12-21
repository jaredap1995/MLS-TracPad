from pymongo import MongoClient
import requests
import json

class ExtractAPIData:
    def __init__(self, GameID) -> None:
        """
        Parameters:
        GameID (str): The unique identifier of the game.
        """

        self.game_id = GameID
        self.client = MongoClient('mongodb://client_url')
        self.db = self.client['db_name']


        self.meta_endpoint = "provided tracab api metadat endpoint ('physical data')"
        self.tac_endpoint = "provided tracab tactical api endpoint"


        self.params = {
            "GameID": self.game_id,
            "VendorID": "your ID",
            "ExtractionVersion": "your ID",
            "DataQuality": "1" # 0 or raw depending on raw or finally processed format
        }

        self.headers = {
            "Provided authorization token"
    }

    def fetch_tactical_data(self):
        """
        Fetches tactical data for a given game. 

        I usually returned the data and saved it as a txt file and then processed it using the TracPad class object,
        though this approach can be modified depending on use case and need.

        Returns:
        dict: The tactical data retrieved from the API.
        """


        response = requests.get(self.tac_endpoint, params=self.params, headers=self.headers)
        response.raise_for_status()

        if response.status_code == 200:
            print('Successful 200 Response. Attempting to retrieve data. This may take a while.')
            print(response.text[:500])
            data = response.text
            return data
        else:
            print("There appears to be an error. The response was ", response)


    def insert_metadata(self):
        """
        Inserts metadata into MongoDB for a given game.
        """

        response = requests.get(self.meta_endpoint, params=self.params, headers=self.headers)
        response.raise_for_status()

        
        collection = self.db['collections_name']

        if response.status_code == 200:
            print('Successful 200 Response. Attempting to retrieve data. This may take a while.')
            data = json.loads(response.text)
            data['_id'] = data.pop('GameID')
            try:
                collection.insert_one(data)
                print('Successfully uploaded data into Mongo')
            except Exception as e:
                print('Error', e)
        else:
            print("There appears to be an error. The response was ", response)
