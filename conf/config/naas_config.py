import os
import pytest
import json


class NaaSConfig(object):
    env = None
    __config__ = None

    def __init__(self):
        self._load_config_file()

        ###Need to add this for any new type of config in json.
        self._server_config = self._merge_configs("server")
        self._customer_choice_config = self._merge_configs("customer_choice")

        self._cassandra_config = self._merge_configs("cassandra_config")
        self._headers = self._merge_configs("headers")

        self._mock_server_config = self._merge_configs("mock_server")
        return

    def _load_config_file(self):
        self.env = os.environ["RUN_ENV"]
        # self.env = "prod"
        __location__ = os.path.realpath(
            os.path.join(os.getcwd(), os.path.dirname(__file__)))
        config_file = os.path.join(__location__, self.env + ".json")
        default_config_file = os.path.join(__location__, "default.json")
        with open(default_config_file) as default_json:
            self.__default_config__ = json.load(default_json)
        with open(config_file) as json_file:
            self.__config__ = json.load(json_file)

    def _merge_configs(self, config_key):
        return {**self.__default_config__.get(config_key, {}), **self.__config__.get(config_key, {})}

    def get_server(self, key):
        return self._server_config.get(key)

    def get_customer_choice_config(self, key):
        return self._customer_choice_config.get(key)

    def get_cassandra_config(self, key):
        return self._cassandra_config.get(key)

    def get_headers(self, key):
        return self._headers.get(key)

    def get_mocke_server_configs(self):
        return self._mock_server_config

if __name__ == '__main__':
    print(__file__)