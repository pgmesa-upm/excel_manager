
import os
import time
import pygame
import platform
from typing import Union

import easygui
import excel
import GUI.display as display
import config
from login import get_login_info, login_salt
from crypt_utilities.asymmetric import load_pem_private_key, load_pem_public_key, RSAPrivateKey
from crypt_utilities.hashes import derive
from editor.protected_data import set_login_password

USER_MODE = 0
ADMIN_MODE = 1

_close = False
_screen = None
_clock = None

def init():
    global _screen, _clock
    
    pygame.init()
    _screen = pygame.display.set_mode(display.screenSize, pygame.RESIZABLE)
    pygame.display.set_caption("Excel Manager")

    _clock = pygame.time.Clock()
    
def check_os():
    global _screen, _clock, _close
    
    while not _close: 
        _screen.fill(display.BLACK)
        if platform.system() != "Windows":
            display.show_msg(_screen, "Este Programa solo funciona en Windows")
        else: return
        _clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                _close = True
            if event.type == pygame.VIDEORESIZE:
                size = (event.w, event.h)
                display.configureScreen(size)
    
def login():
    global _screen
    
    check_os()
    # Cargamos la contraseña
    hashed_pw, salt = get_login_info()
    
    text_box = display.showInput(_screen, 2)
    msg = None
    while not _close: 
        _screen.fill(display.BLACK); valid_password = False
        display.show_msg(_screen, "Introduce la clave de acceso al programa:")
        _clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.VIDEORESIZE:
                size = (event.w, event.h)
                display.configureScreen(size)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                login_pass = text_box.text
                hashed_in = derive(login_pass.encode(), login_salt)
                if hashed_in == hashed_pw:
                    valid_password = True
                    msg = "Iniciando el Programa"
                    key = derive(login_pass.encode(), salt)
                    set_login_password(key)
                else:
                    msg = "Contraseña Incorrecta"
            # Vemos si han escrito en el input
            text_box.handle_event(event)
        if not valid_password:
            # Vemos si hay que actualizar el tamaño
            text_box.update()
            # Refrescamos el render del inputbox
            text_box.draw(_screen)
        if msg is not None:
            order = 2 if valid_password else 5
            color = display.RED if not valid_password else display.LIGHT_GREEN
            display.show_msg(_screen, msg, color=color, order=order)
        
        pygame.display.update()
        # Dejamos que el usuario vea la info y devolvemos la clave privada
        if valid_password:
            time.sleep(0.5)
            return 0

def select_mode() -> int:
    global _screen, _close
    
    while not _close:
        _screen.fill(display.BLACK)
        _clock.tick(60) # Se establecen el frame rate (fps)
        buttons = display.showOptions(_screen)  
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.VIDEORESIZE:
                size = (event.w, event.h)
                display.configureScreen(size)
            if event.type == pygame.MOUSEBUTTONDOWN:
                for but in buttons:
                    if but.collidepoint(pygame.mouse.get_pos()):
                        if buttons.index(but) == 1:
                            return USER_MODE
                        elif buttons.index(but) == 2:
                            return ADMIN_MODE
        pygame.display.update()

def select_user_action() -> Union[str, None]:
    global _screen, _close
    
    while not _close:
        _screen.fill(display.BLACK)
        _clock.tick(60) # Se establecen el frame rate (fps)
        
        buttons = display.show_user_actions(_screen)  
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.VIDEORESIZE:
                size = (event.w, event.h)
                display.configureScreen(size)
            if event.type == pygame.MOUSEBUTTONDOWN:
                for but in buttons:
                    if but.collidepoint(pygame.mouse.get_pos()):
                        if buttons.index(but) == 1:
                            return "add"
                        elif buttons.index(but) == 2:
                            return "check"
        pygame.display.update()

def ask_private_key() -> tuple[bool, Union[RSAPrivateKey, None]]:
    global _screen, _close
    private_key = None
    
    msg = "Selecciona el fichero que contiene la clave privada (RSA)"
    _screen.fill(display.BLACK)
    display.show_msg(_screen, msg)
    pygame.display.update()
    
    key_file_path = easygui.fileopenbox(default=os.getcwd())
    
    text_box = display.showInput(_screen, 2)
    msg = None
    correct_key = False
    
    while not _close:
        _screen.fill(display.BLACK)
        display.show_msg(_screen, "Introduce la clave con la que se serializo la clave privada: ")
        _clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False, private_key
            if event.type == pygame.VIDEORESIZE:
                size = (event.w, event.h)
                display.configureScreen(size)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                password = text_box.text
                if password == "": password = None
                else: password = password.encode()
                try:
                    private_key = load_pem_private_key(key_file_path, password=password)
                except:
                    msg = "Credenciales Incorrectos (revisa el fichero introducido o la contraseña)"
                else:
                    msg = "Credenciales Correctos"
                    correct_key = True
            # Vemos si han escrito en el input
            text_box.handle_event(event)
        if not correct_key:
            # Vemos si hay que actualizar el tamaño
            text_box.update()
            # Refrescamos el render del inputbox
            text_box.draw(_screen)
        if msg is not None:
            order = 2 if correct_key else 5
            color = display.RED if not correct_key else display.LIGHT_GREEN
            display.show_msg(_screen, msg, color=color, order=order)
        
        pygame.display.update()
        # Dejamos que el usuario vea la info y devolvemos la clave privada
        if correct_key:
            time.sleep(2); return correct_key, private_key
        
    return True, private_key

def start_editor(private_key:RSAPrivateKey=None):
    global _screen, _close
    excel_path = excel.get_excel_path()
    print(excel_path)
    if not os.path.exists(excel_path):
        raise Exception(f"No existe el fichero '{excel_path.name}' en la ruta especificada '{excel.data_dir_name}'")
    if excel.empty() and private_key is None:
        raise Exception(f"El archivo '{excel_path.name}' esta vacio, csv editor no permitido")
    
    public_key = load_pem_public_key(excel.main_execution_path/config.get("public_key_path"))
    key_pairs = (private_key, public_key)
 
    msg = "Editor abierto, cierralo para poder cerrar el programa"
    _screen.fill(display.BLACK)
    display.show_msg(_screen, msg)
    pygame.display.update()
    # 
    csv_sheets:dict = excel.refresh_csv_sheets()
    # abrimos el editor que corresponda (intentamos excel y si no el custom csveditor)
    def open_csveditor():
        display.showCustomEditor(
            csv_group_label='Study Groups',
            csv_paths=csv_sheets,
            rsa_key_pairs=key_pairs,
            sensitive_fields=config.get('sensitive_fields', else_return=[]),
            hide_fields=config.get('hide_fields_from_users', else_return=[])
        )
        
    excel.backup()
    if private_key is not None:
        editor_preference = config.get("admin_editor_preference")
        if editor_preference == 'excel':
            excel.decrypt_excel(private_key)
            launched = excel.launch()
            if not launched:
                excel.protect_sensitive_data(public_key)
                if excel.empty():
                    raise Exception("El archivo patients_data.xlsx esta vacio, csv editor no permitido")
                open_csveditor()
            else:
                stop = False
                while not excel.check() or not stop:
                    _screen.fill(display.BLACK)
                    display.show_msg(_screen, msg)
                    pygame.display.update()
                    _clock.tick(60)
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            stop = True
                        if event.type == pygame.VIDEORESIZE:
                            size = (event.w, event.h)
                            display.configureScreen(size)
                _screen.fill(display.BLACK)
                display.show_msg(_screen, "Encriptando y Guardando (puede tardar)...")
                pygame.display.update()
                excel.protect_sensitive_data(public_key)
                excel.refresh_csv_sheets()
        else:
            if excel.empty():
                raise Exception("El archivo patients_data.xlsx esta vacio, csv editor no permitido")
            open_csveditor()
            _close = True
    else:
        _close = True
        open_csveditor()
    try:
        excel.update_excel()
    except PermissionError:
        print("[%] Error, permission denied (excel is opened)")
        stop = False
        while not excel.check() or not stop:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    stop = True
                if event.type == pygame.VIDEORESIZE:
                    size = (event.w, event.h)
                    display.configureScreen(size)
            _screen.fill(display.BLACK)
            display.show_msg(_screen, "PERMISSION DENIED: El excel se encuentra abierto, cierrelo para poder actualizarlo")
            pygame.display.update()
        if excel.check():
            _screen.fill(display.BLACK)
            display.show_msg(_screen, "Actualizando excel...")
            pygame.display.update()
            excel.update_excel()

def _check_id_field():
    id_field = config.get('id_field')
    if id_field is not None: return 0
    while True:
        _screen.fill(display.BLACK)
        display.show_msg(_screen, "El campo 'id_field' en .config.json esta vacio, no se ha especificado un campo identificador")
        _clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 1
            if event.type == pygame.VIDEORESIZE:
                size = (event.w, event.h)
                display.configureScreen(size)
        pygame.display.update()
    
def check_id() -> str:
    global _screen, _close
    
    outcome = _check_id_field()
    if outcome != 0: return
    id_field = config.get('id_field')
    text_box = display.showInput(_screen, 2)
    msg = None

    while not _close:
        _screen.fill(display.BLACK)
        display.show_msg(_screen, f"Introduce el valor del '{id_field}' a comprobar:")
        _clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.VIDEORESIZE:
                size = (event.w, event.h)
                display.configureScreen(size)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                id_value = text_box.text
                found = excel.check_id_value(id_value)
                if len(found) == 0:
                    msg = "No se encontraron coincidencias en el excel"
                else:
                    sheets = list(found.keys())
                    lines = list(found.values())
                    msg = f"Se encontraron coincidencias en las hojas '{sheets}' => líneas: {lines}"
            # Vemos si han escrito en el input
            text_box.handle_event(event)
        # Vemos si hay que actualizar el tamaño
        text_box.update()
        # Refrescamos el render del inputbox
        text_box.draw(_screen)
        if msg is not None:
            order = 5
            color = display.RED if not found else display.LIGHT_GREEN
            display.show_msg(_screen, msg, color=color, order=order)
        
        pygame.display.update()

def error(msg:str):
    global _screen, _close, _screen

    while not _close:
        _screen.fill(display.BLACK)
        _clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                _close = True
                return
            if event.type == pygame.VIDEORESIZE:
                size = (event.w, event.h)
                display.configureScreen(size)
        # Mostrar mensaje de Excel abierto
        display.show_msg(_screen, "ERROR: " + msg)
        pygame.display.update()
       
def close():
    pygame.quit()






