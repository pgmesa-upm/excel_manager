
import os
import json
import shutil
from typing import Any, Union
from pathlib import Path

config_dir = '.config'
config_fname = 'config.json'
default_config_fname = 'default_config.json'
config_file_path = Path(os.getcwd()).resolve()/config_dir/config_fname
default_config_file_path = Path(os.getcwd()).resolve()/config_dir/default_config_fname


def get(dict_key:str=None) -> Union[Any, None]:
    if not os.path.exists(config_file_path):
        shutil.copy(default_config_file_path, config_file_path)
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