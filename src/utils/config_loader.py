import yaml

class ConfigLoader:
    @staticmethod
    def load_config(file_path: str) -> dict:
        with open(file_path, 'r') as file:
            return yaml.safe_load(file)