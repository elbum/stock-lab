from pymongo import MongoClient
from pymongo.cursor import CursorType
import configparser


class MongoDBHandler:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('conf/config.ini')
        host = config['MONGODB']['host']
        port = config['MONGODB']['port']

        self._client = MongoClient(host, int(port))

    def insert_item(self, data, db_name=None, collection_name=None):
        if not isinstance(data, dict):
            raise Exception("data should be dict")
        if db_name is None or collection_name is None:
            raise Exception("Need to param db_name,collection_name")

        return self._client[db_name][collection_name].insert_one(data).inserted_id

    def insert_items(self, data, db_name=None, collection_name=None):
        if not isinstance(data, list):
            raise Exception("data should be list")
        if db_name is None or collection_name is None:
            raise Exception("Need to param db_name,collection_name")

        return self._client[db_name][collection_name].insert_many(data).inserted_ids

    def find_items(self, condition=None, db_name=None, collection_name=None):
        if condition is None or not isinstance(condition, dict):
            condition = {}
        if db_name is None or collection_name is None:
            raise Exception("Need to param db_name, collection_name")

        return self._client[db_name][collection_name].find(condition, no_cursor_timeout=True, cursor_type=CursorType.EXHAUST)

    def find_item(self, condition=None, db_name=None, collection_name=None):
        if condition is None or not isinstance(condition, dict):
            condition = {}
        if db_name is None or collection_name is None:
            raise Exception("Need to param db_name, collection_name")

        return self._client[db_name][collection_name].find_one(condition)

    def delete_items(self, condition=None, db_name=None, collection_name=None):
        if condition is None or not isinstance(condition, dict):
            raise Exception("Need to condition")
        if db_name is None or collection_name is None:
            raise Exception("Need to param db_name, collection_name")

        return self._client[db_name][collection_name].delete_many(condition)

    def update_item(self, condition=None, update_value=None, db_name=None, collection_name=None):
        if condition is None or not isinstance(condition, dict):
            raise Exception("Need to condition")
        if update_value is None:
            raise Exception("Need to update value")
        if db_name is None or collection_name is None:
            raise Exception("Need to param db_name , collection_name")
        return self._client[db_name][collection_name].update_one(filter=condition, update=update_value, upsert=True)

    def update_items(self, condition=None, update_value=None, db_name=None, collection_name=None):
        if condition is None or not isinstance(condition, dict):
            raise Exception("Need to condition")
        if update_value is None:
            raise Exception("Need to update value")
        if db_name is None or collection_name is None:
            raise Exception("Need to param db_name , collection_name")
        return self._client[db_name][collection_name].update_many(filter=condition, update=update_value)

    def aggregate(self, pipeline=None, db_name=None, collection_name=None):
        if pipeline is None or not isinstance(pipeline, list):
            raise Exception("Need pipeline")
        if db_name is None or collection_name is None:
            raise Exception("Need to param db_name, collection_name")
        return self._client[db_name][collection_name].aggregate(pipeline)

    def text_search(self, text=None, db_name=None, collection_name=None):
        if text is None or not isinstance(text, str):
            raise Exception("Need string text")
        if db_name is None or collection_name is None:
            raise Exception("Need to param db_name,collection_name")
        return self._client[db_name][collection_name].find({"$text": {"$search": text}})
