
import os
import pickle
from typing import Union
from pathlib import Path

from crypt_utilities.hashes import derive, generate_salt
from crypt_utilities.symmetric import encrypt, decrypt

main_execution_path = Path(__file__).resolve().parent.parent
data_dir = './.data'
data_dir_path = main_execution_path/data_dir
if not os.path.exists(data_dir_path): os.mkdir(data_dir_path)
pd_fname = '.protected_data'
hashed_ids_fname = '.hashed_ids'
pd_file_path = data_dir_path/pd_fname
hashed_ids_file_path = data_dir_path/hashed_ids_fname

login_password:bytes = None
# Pocas iteraciones puesto que lo importante es que la contraseña principal este segura
# estos hashes no nos preocupa tanto que se puedan crackear ya que estan encriptados
# asi ganamos eficiencia en el programa
num_iters_hashes = 100
# Aqui tambien pocas, puesto que estamso hasheando el texto encriptado, y solo lo hacemos
# no obtener colisiones (se podria haber usado un hasheado normal sin sal)
num_iters_encr = 100

def set_login_password(password:bytes):
    global login_password
    login_password = password

def get_login_password() -> bytes:
    global login_password
    return login_password

def get_encrypted(hash_key:bytes=None) -> Union[bytes, None]:
    if not os.path.exists(pd_file_path): 
        return None
    else:
        with open(pd_file_path, 'rb') as file:
            register = pickle.load(file)
    
    encrypted = register
    if hash_key is not None:
        try: encrypted = register[hash_key]
        except KeyError: return None
        
    return encrypted

def get_sheet_hashed_ids(sheet_name:str=None, decrypt_hashes:bool=True) -> Union[dict, list, None]:
    global login_password
    if not os.path.exists(hashed_ids_file_path): 
        return None
    with open(hashed_ids_file_path, 'rb') as file:
        dict_of_hashes = pickle.load(file)
    if decrypt_hashes:
        decrypted_dict = {}
        for sheet_n, hashes in dict_of_hashes.items():
            decrypted_dict[sheet_n] = []
            for hash_ in hashes:
                for encr_hash, salt in hash_.items():
                    decrypted_hash = decrypt(encr_hash, login_password)
                    decrypted_dict[sheet_n].append({decrypted_hash: salt})
        dict_of_hashes = decrypted_dict
    
    if sheet_name is not None:
        dict_of_hashes = dict_of_hashes[sheet_name]
    return dict_of_hashes

def hash_sheet_ids_and_save(sheet_name:str, colum:list, override:bool=True):
    global login_password
    dic = {sheet_name: []}
    for elem in colum:
        salt = generate_salt()
        hashed_elem = derive(str(elem).encode(), salt, iterations=num_iters_hashes)
        encr = encrypt(hashed_elem, login_password)
        dic[sheet_name].append({encr:salt})
    assert len(colum) == len(dic[sheet_name])
    dict_of_hashes = get_sheet_hashed_ids(decrypt_hashes=False)
    if dict_of_hashes is None:
        dict_of_hashes = dic
    else:
        if override or sheet_name not in dict_of_hashes:
            dict_of_hashes[sheet_name] = dic[sheet_name]
        else:
            dict_of_hashes[sheet_name] += dic[sheet_name]
    with open(hashed_ids_file_path, 'wb') as file:
        pickle.dump(dict_of_hashes, file)

def hash_and_save_encrypted(ciphertext:bytes, length:int=10) -> bytes:
    register = get_encrypted()
    if register is None:
        register = {}
    salt = generate_salt()
    salted_hash = derive(ciphertext, salt, length=length, iterations=num_iters_encr)
    register[salted_hash] = ciphertext
    with open(pd_file_path, 'wb') as file:
        pickle.dump(register, file)

    return salted_hash

if __name__ == "__main__":
    #print(get_encrypted())
    print(get_sheet_hashed_ids(decrypt_hashes=True))
    # hashed = hash_and_save_encrypted("hola".encode())
    # recovered = get_encrypted(hashed).decode()
    # print(recovered)