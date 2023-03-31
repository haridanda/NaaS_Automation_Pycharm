
import os,json,copy

class DataProvider(object):
    env = None
    _data = {}

    def load_json_from_file(self,file_path):
        with open(file_path) as json_file:
            return json.load(json_file)

    def _get_data_file_full_path(self,file):
        path =  os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(file)))
        return os.path.join(path,self.env + ".json")

    def _get_default_data_file_full_path(self,file):
        path =  os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(file)))
        return os.path.join(path + "/prod-glass.json")

    def __init__(self,file=None,load_root_data=True):
        self.env = os.environ["RUN_ENV"]
        #self.env = "prod"
        root_data_path = self._get_data_file_full_path(__file__)
        file_exists = os.path.exists(root_data_path)

        if file_exists and load_root_data:
            self._data = self.load_json_from_file(root_data_path)
        else:
            root_data_path = self._get_default_data_file_full_path(__file__)
            self._data = self.load_json_from_file(root_data_path)

        if file:
            data_path = self._get_data_file_full_path(file)
            self._data = {**self._data, **self.load_json_from_file(data_path)}
        return

    def get_data_node(self, node):
        return self._data.get(node)

    def get_nested_node(self,nested_node=[]):
        ret_val = self._data
        for each in nested_node:
            ret_val = ret_val.get(each)
        return copy.deepcopy(ret_val)