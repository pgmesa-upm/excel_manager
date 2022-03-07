import os
import pickle
from typing import Union
from pathlib import Path

from editor.protected_data import hashed_ids_file_path

from crypt_utilities.hashes import generate_salt, derive

login_salt = b'b\x993\x80\xa6"\xb7H\xb50\tU>r5V\xc8\t\xb4\xde;{[\xdd'

data_dir = './.data'
login_fname = '.login'
main_executable_path = Path(__file__).resolve().parent
login_file_path = main_executable_path/data_dir/login_fname

def get_login_info() -> Union[tuple[bytes,bytes], tuple[None,None]]:
    if not os.path.exists(login_file_path):
        return None, None
    with open(login_file_path, 'rb') as file:
        login_dict:dict = pickle.load(file)
    hashed_pw = list(login_dict.keys())[0]
    salt = list(login_dict.values())[0]
    return hashed_pw, salt

def init_login():
    global login_salt
    if os.path.exists(hashed_ids_file_path):
        print(f"Deleting '{hashed_ids_file_path}'...")
        os.remove(hashed_ids_file_path)
    valid_pw = False
    while not valid_pw:
        password = str(input("Introduce the password of the program: "))
        if password == "":
            print("[!] Password can't be void")
            continue
        print(f"-> '{password}'")
        confirmation = str(input("Repeat the password: "))
        print(f"-> '{confirmation}'")
        if password != confirmation:
            print("[!] Passwords don't match")
        else:
            valid_pw = True
    print("Saving password...")
    with open(login_file_path, 'wb') as file:
        hashed = derive(password.encode(), login_salt)
        # Salt to use after to obtain the real key
        salt = generate_salt()
        pickle.dump({hashed: salt}, file)