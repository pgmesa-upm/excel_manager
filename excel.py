
import os
from math import isnan
import openpyxl as pyxl
from openpyxl.utils import column_index_from_string
import datetime as dt
from pathlib import Path
import pandas as pd
from pandas.core.frame import DataFrame
from subprocess import Popen, PIPE, run
from typing import Union

import config
from editor.encryption import rsa_encrypt, RSAPublicKey, RSAPrivateKey, rsa_decrypt
from editor.protected_data import hash_and_save_encrypted, get_encrypted

data_dir_name = '.data'
backup_dir = '.backup'
data_dir_path = Path(data_dir_name).resolve()

date_format = config.get('date_format', else_return='%d/%m/%Y')

def get_excel_path() -> Path:
    excel_path = config.get('excel_path')
    if excel_path != None: excel_path = Path(excel_path).resolve()
    return excel_path

def launch() -> bool:
    process = run(f'start excel "{get_excel_path()}"', shell=True, cwd=os.getcwd(), stdout=PIPE, stderr=PIPE)
    if process.returncode == 0:
        return True
    return False
    
def refresh_csv_sheets() -> tuple[list, list]:
    print("[%] Refreshing csv sheets...")
    if empty(): return
    excel_path = get_excel_path()
    excel = pd.ExcelFile(excel_path)
    sheet_names = excel.sheet_names; sheets_info = {}
    # Eliminamos las que ya no exitan en el excel (cambio de nombre o eliminadas)
    existing_sh_names = list_csv_sheets()
    for ex_sh in existing_sh_names:
        if ex_sh not in sheet_names:
            os.remove(data_dir_path/(ex_sh+".csv"))
    
    for sheet_name in sheet_names:
        sheet:DataFrame = excel.parse(sheet_name)
        sheet_dest_path = data_dir_path/(sheet_name+".csv")
        sheets_info[sheet_name] = sheet_dest_path
        sheet.to_csv(sheet_dest_path, index=False, date_format=date_format)
        sheet.columns
        
    return sheets_info

def list_csv_sheets() -> list:
    filtered = filter(lambda f: f.endswith('.csv'), os.listdir(data_dir_path))
    return list(map(lambda f: f.removesuffix('.csv'), filtered))
    
def update_excel():
    print("[%] Updating excel from csv sheets...")
    if empty(): return
    csv_sheet_names = list_csv_sheets()
    sheets_dict = {}
    for sheet_name in csv_sheet_names:
        df = pd.read_csv(data_dir_path/(sheet_name+".csv"))
        csv_dict = df.to_dict("list")
        sheets_dict[sheet_name] = csv_dict
    wb = pyxl.load_workbook(get_excel_path())
    _write_dict_into_wb(wb, sheets_dict, encrypted=True)
            
def _parse_elem(elem:str, dtype:str) -> any:
    try:
        # Los numeros mejor no convertirlos
        if dtype == 'int':
            return int(elem)
        elif dtype == 'float':
            return float(elem)
        elif dtype == 'str-q':
            if not str(elem).startswith("'"):
                return "'"+str(elem)
    except: pass
    return str(elem) 

def isempty(elem:any) -> bool:
    is_nan = False
    try: is_nan = isnan(elem)
    except: pass
    return elem == "" or elem is None or is_nan

def _write_dict_into_wb(wb:pyxl.Workbook, sheets_dict:dict, encrypted=False):
    print("[%] Writing into excel sheets...")
    data_types:list = config.get('data_types')
    sfields:list = config.get('sensitive_fields')
    if sfields is None: sfields = []
    # Guardar por celdas en cada ws  
    excel_path = get_excel_path()
    wb = pyxl.load_workbook(excel_path)
    for sheet_name, sheet_info in sheets_dict.items():
        ws = wb[sheet_name]
        for colum, header in enumerate(sheet_info.keys(),1):
            dtype = None
            if data_types is not None and header in data_types:
                dtype = data_types[header]
            colum_elements = sheet_info[header]
            ws.cell(1, colum).value = header
            for row, elem  in enumerate(colum_elements, 2):
                if not encrypted or not header in sfields:
                    if isempty(elem): 
                        elem = ""
                    elif dtype is not None:
                        elem = _parse_elem(elem, dtype)
                ws.cell(row, colum).value = elem
    wb.save(excel_path)
             
def backup():
    print("[%] Executing excel backup...")
    try:
        backup_path = data_dir_path/backup_dir
        if not os.path.exists(backup_path):
            os.mkdir(backup_path)
        with open(get_excel_path(), 'rb') as file:
            content = file.read()
        bname = _get_date(path_friendly=True)+".xlsx"
        with open(backup_path/bname, 'wb') as file:
            file.write(content)
    except FileNotFoundError: pass

def decrypt_excel(private_key:RSAPrivateKey):
    print("[%] Decrypting excel fields...")
    if empty(): return
    sfields = config.get('sensitive_fields')
    excel_path = get_excel_path()
    excel = pd.ExcelFile(excel_path)
    sheet_names = excel.sheet_names
    decrypted_sheets = {}
    for sheet_name in sheet_names:
        sheet:DataFrame = excel.parse(sheet_name)
        csv_dict = sheet.to_dict("list")
        decrypted_sheet = {}
        for header in csv_dict:
            colum = csv_dict[header]
            decrypted_colum = []
            for elem in colum:
                if isempty(elem): elem = ""
                elem = str(elem)
                ciphertext = get_encrypted(elem.encode()); 
                if ciphertext is not None:
                    elem = rsa_decrypt(ciphertext, private_key).decode()
                decrypted_colum.append(elem)
            colum = decrypted_colum
            decrypted_sheet[header] = colum
        decrypted_sheets[sheet_name] = decrypted_sheet
    
    wb = pyxl.load_workbook(excel_path)
    _write_dict_into_wb(wb, decrypted_sheets)
       

def protect_sensitive_data(public_key:RSAPublicKey):
    print("[%] Encrypting excel data...")
    if empty(): return
    sfields:list = config.get('sensitive_fields')
    if sfields is None: sfields = []
    excel = pd.ExcelFile(get_excel_path())
    sheet_names = excel.sheet_names
    protected_sheets = {}
    for sheet_name in sheet_names:
        sheet:DataFrame = excel.parse(sheet_name)
        csv_dict = sheet.to_dict("list")
        protected_sheet = {}
        for header in csv_dict:
            colum = csv_dict[header]
            # Encriptamos datos sensibles
            if header in sfields:
                protected_colum = []
                for elem in colum:
                    if isempty(elem): 
                        elem = ""
                    else:
                        elem = str(elem)
                        encrypted = get_encrypted(elem.encode())
                        if encrypted is None:
                            elem = str(elem)
                            ciphertext = rsa_encrypt(elem.encode(), public_key)
                            salted_hash = hash_and_save_encrypted(ciphertext)
                            elem = salted_hash.decode()
                    protected_colum.append(elem)
                colum = protected_colum
            protected_sheet[header] = colum
        protected_sheets[sheet_name] = protected_sheet
    # Guardar por celdas en cada ws  
    wb = pyxl.load_workbook(get_excel_path())
    _write_dict_into_wb(wb, protected_sheets, encrypted=True)
        
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
        open(get_excel_path(), 'r+')
    except IOError:
        # El excel sigue abierto
        return False
    else:
        return True
    
def empty():
    df = pd.read_excel(get_excel_path())
    return df.empty
    
if __name__ == "__main__":
    # update_excel()
    # refresh_csv_sheets()
    # from editor.encryption import load_pem_public_key, load_pem_private_key
    # public_key = load_pem_public_key(config.get('public_key_path'))
    # private_key = load_pem_private_key('private_key', password='Prueba'.encode())
    # decrypt_excel(private_key)
    # protect_sensitive_data(public_key)
    #get_excel_sheets_as_csv()
    refresh_csv_sheets()
    
# def get_excel_sheets_as_csv():
#     excel_path = get_excel_path()
#     wb = pyxl.load_workbook(excel_path)
#     sheet_names = wb.sheetnames
#     for sheet in sheet_names:
#         if sheet != 'CONTROL': continue
#         ws = wb[sheet]
#         start, end = ws.calculate_dimension().split(":")
#         start_row = column_index_from_string(start[0]); end_row = column_index_from_string(end[0])
#         start_column = int(start[1:]); end_column = int(end[1:])
#         for row_index in range(start_row, end_row):
#             row_str = ""
#             for column_index in range(start_column, end_column):
#                 cell_val = ws.cell(row_index, column_index).value
#                 print(cell_val)
                
# def df_to_csv(df:DataFrame, filepath:Union[str,Path]=None) -> str:
#     """Parseador de Pandas Dataframe a csv sin ningun tipo de parseador de datos de 
#     pandas, (util para fechas en un formato especifico)"""
#     headers = list(df.columns.values)
#     csv_str = ""
#     df = df.reset_index()  # make sure indexes pair with number of rows
    
#     def iter_rows(df) -> str:
#         for index, row in df.iterrows():
#             row_str = ""
#             for h in headers:
#                 val = row[h]
#                 print(val, str(val))
#                 if index == len(headers)-1:
#                     row_str += str(val)
#                 else: 
#                     row_str += str(val) + ","
#             yield row_str+"\n"

#     if filepath is None:
#         for row in iter_rows(df):
#             csv_str += row  
#     else:
#         with open(filepath, 'w') as csvfile:
#             for row in iter_rows(df):
#                 csv_str += row  
#                 csvfile.write(row)
#     return csv_str