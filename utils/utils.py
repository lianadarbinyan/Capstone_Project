import os

class ConfigReader:
    def __init__(self, file_path):
        self.properties = {}
        self.load_properties(file_path)

    def load_properties(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        key_value = line.split('=', 1)
                        if len(key_value) == 2:
                            self.properties[key_value[0].strip()] = key_value[1].strip()
        else:
            print(f"File not found: {file_path}")

    def get_property(self, key):
        return self.properties.get(key)

    def get_properties(self):
        return self.properties.copy()
