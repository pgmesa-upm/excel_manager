
import os
import json
import datetime as dt
from pathlib import Path
import pandas as pd
from pandas.core.frame import DataFrame
from subprocess import Popen, PIPE, run

import config
from editor.encryption import rsa_encrypt, RSAPublicKey, RSAPrivateKey, rsa_decrypt
from editor.protected_data import hash_and_save_encrypted, get_encrypted

data_dir_name = '.data'
backup_dir = '.backup'
excel_name = 'patients_data.xlsx'
data_dir_path = Path(data_dir_name).resolve()
excel_path = data_dir_path/excel_name

def launch() -> bool:
    process = run(f'start excel "{excel_path}"', shell=True, cwd=os.getcwd(), stdout=PIPE, stderr=PIPE)
    if process.returncode == 0:
        return True
    return False
    
def refresh_csv_sheets() -> tuple[list, list]:
    if empty(): return
    excel = pd.ExcelFile(excel_path)
    sheet_names = excel.sheet_names; sheets_info = {}
    for sheet_name in sheet_names:
        sheet:DataFrame = excel.parse(sheet_name)
        sheet_dest_path = data_dir_path/(sheet_name+".csv")
        sheets_info[sheet_name] = sheet_dest_path
        sheet.to_csv(sheet_dest_path, index=False)
        
    return sheets_info
    
def update_excel():
    if empty(): return
    csv_sheet_names = os.listdir(data_dir_path)
    with pd.ExcelWriter(excel_path) as writer:
        for sheet_name in csv_sheet_names:
            if not sheet_name.endswith('.csv'): continue
            df = pd.read_csv(data_dir_path/sheet_name)
            sheet_name = sheet_name.removesuffix('.csv')
            df.to_excel(writer, sheet_name=sheet_name, index=False)
                   
def backup():
    try:
        backup_path = data_dir_path/backup_dir
        if not os.path.exists(backup_path):
            os.mkdir(backup_path)
        with open(excel_path, 'rb') as file:
            content = file.read()
        bname = _get_date(path_friendly=True)+".xlsx"
        with open(backup_path/bname, 'wb') as file:
            file.write(content)
    except FileNotFoundError: pass

def decrypt_excel(private_key:RSAPrivateKey):
    if empty(): return
    sfields = config.get('sensitive_fields')
    excel = pd.ExcelFile(excel_path)
    sheet_names = excel.sheet_names
    decrypted_sheets = {}
    for sheet_name in sheet_names:
        sheet:DataFrame = excel.parse(sheet_name)
        csv_dict = sheet.to_dict("list")
        decrypted_sheet = {}
        for header in csv_dict:
            colum = csv_dict[header]
            if header in sfields:
                decrypted_colum = []
                for elem in colum:
                    elem = str(elem)
                    empty_elem = elem == "" or elem is None or elem == "nan"
                    if empty_elem: elem = ""
                    ciphertext = get_encrypted(elem.encode()); 
                    if ciphertext is not None:
                        elem = rsa_decrypt(ciphertext, private_key).decode()
                    decrypted_colum.append(elem)
                colum = decrypted_colum
            decrypted_sheet[header] = colum
        
        df:DataFrame = pd.DataFrame.from_dict(decrypted_sheet, orient='columns') # columns is default
        # print(df.to_json(indent=4))
        decrypted_sheets[sheet_name] = df
        
    with pd.ExcelWriter(excel_path) as writer:
        for sheet_name, df in decrypted_sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)   

def protect_sensitive_data(public_key:RSAPublicKey):
    if empty(): return
    sfields = config.get('sensitive_fields')
    excel = pd.ExcelFile(excel_path)
    sheet_names = excel.sheet_names
    protected_sheets = {}
    for sheet_name in sheet_names:
        sheet:DataFrame = excel.parse(sheet_name)
        csv_dict = sheet.to_dict("list")
        protected_sheet = {}
        for header in csv_dict:
            colum = csv_dict[header]
            if header in sfields:
                protected_colum = []
                for elem in colum:
                    elem = str(elem)
                    encrypted = get_encrypted(elem.encode())
                    empty_elem = elem == "" or elem is None or elem == "nan"
                    if not empty_elem and encrypted is None:
                        ciphertext = rsa_encrypt(elem.encode(), public_key)
                        salted_hash = hash_and_save_encrypted(ciphertext)
                        elem = salted_hash.decode()
                    if empty_elem: elem = ""
                    protected_colum.append(elem)
                colum = protected_colum
            protected_sheet[header] = colum

        df:DataFrame = pd.DataFrame.from_dict(protected_sheet, orient='columns') # columns is default
        # print(df.to_json(indent=4))
        protected_sheets[sheet_name] = df
        
    with pd.ExcelWriter(excel_path) as writer:
        for sheet_name, df in protected_sheets.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        
def _get_date(path_friendly:bool=False) -> str:
    datetime = dt.datetime.now()
    if path_friendly:
        date = str(datetime.date())
        time = str(datetime.time()).replace(':', "-").replace('.', '_')
        return date+"_"+time
    else:
        return str(datetime)
        
def check():
    try:
        open(excel_path, 'r+')
    except IOError:
        # El excel sigue abierto
        return False
    else:
        return True
    
def empty():
    df = pd.read_excel(excel_path)
    return df.empty
    
if __name__ == "__main__":
    # update_excel()
    # refresh_csv_sheets()
    from editor.encryption import load_pem_public_key, load_pem_private_key
    public_key = load_pem_public_key(config.get('public_key_path'))
    private_key = load_pem_private_key('private_key', password='Prueba'.encode())
    # decrypt_excel(private_key)
    protect_sensitive_data(public_key)