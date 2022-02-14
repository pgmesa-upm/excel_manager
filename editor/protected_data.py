
import os
from typing import Union
from pathlib import Path
import pickle as pkl

from crypt_utilities.hashes import derive, generate_salt

data_dir = '.data'
pd_fname = '.protected_data'
pd_file_path = Path(os.getcwd()).resolve()/data_dir/pd_fname

def get_encrypted(hash_key:bytes=None) -> Union[bytes, None]:
    if not os.path.exists(data_dir): os.mkdir(data_dir)
    if not os.path.exists(pd_file_path): 
        return None
    else:
        with open(pd_file_path, 'rb') as file:
            register = pkl.load(file)
    
    encrypted = register
    if hash_key is not None:
        try: encrypted = register[hash_key]
        except KeyError: return None
        
    return encrypted


def hash_and_save_encrypted(ciphertext:bytes, length:int=10) -> bytes:
    register = get_encrypted()
    if register is None:
        register = {}
    
    salt = generate_salt()
    salted_hash = derive(ciphertext, salt, length=length, iterations=100)
    
    register[salted_hash] = ciphertext
    with open(pd_file_path, 'wb') as file:
        pkl.dump(register, file)
    
    return salted_hash

if __name__ == "__main__":
    print(get_encrypted())
    # hashed = hash_and_save_encrypted("hola".encode())
    # recovered = get_encrypted(hashed).decode()
    # print(recovered)