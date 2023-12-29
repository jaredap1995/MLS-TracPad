from pymongo import MongoClient
import requests
import json

class ExtractAPIData:
    def __init__(self, GameID, client, db, collection, header, vendorID, ExtractionVersion, dataQuality, meta_endpoint, tac_endpoint):
        self.game_id = GameID
        self.client = MongoClient(client)
        self.db = self.client[db]
        self.collection = self.db[collection]

        self.meta_endpoint = meta_endpoint
        self.tac_endpoint = tac_endpoint

        self.params = {
            "GameID": self.game_id,
            "VendorID": vendorID,
            "ExtractionVersion": ExtractionVersion,
            "DataQuality": dataQuality
        }

        self.headers = {
            "Authorization": header
        }

    def fetch_tactical_data(self):
        response = requests.get(self.tac_endpoint, params=self.params, headers=self.headers)
        response.raise_for_status()

        if response.status_code == 200:
            print('Successful 200 Response. Attempting to retrieve data. This may take a while.')
            print(response.text[:500])
            return response.text
        else:
            print("There appears to be an error. The response was ", response)

    def fetch_metadata(self):
        response = requests.get(self.meta_endpoint, params=self.params, headers=self.headers)
        response.raise_for_status()

        if response.status_code == 200:
            print('Successful 200 Response. Attempting to retrieve data. This may take a while.')
            return json.loads(response.text)
        else:
            print("There appears to be an error. The response was ", response)
            return None
