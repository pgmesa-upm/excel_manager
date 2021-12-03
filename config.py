
import os
import json
from typing import Any, Union
from pathlib import Path

config_dir = '.config'
config_fname = 'config.json'
config_file_path = Path(os.getcwd()).resolve()/config_dir/config_fname


def get(dict_key:str=None) -> Union[Any, None]:
    with open(config_file_path, 'r') as file:
        config_dict:dict = json.load(file)
        
    info = config_dict
    if dict_key is not None:
        try: info = config_dict[dict_key]
        except KeyError: return None
    
    return info
        
# Pruebas de que todo funciona
if __name__ == "__main__":
    ...