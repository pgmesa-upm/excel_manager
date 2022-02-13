
import os
import time
import pygame
import platform
from typing import Union

import easygui
import excel
import GUI.display as display
import config
from editor.encryption import load_pem_private_key, load_pem_public_key, RSAPrivateKey


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

def update_msg():
    ...

def select_mode() -> int:
    global _screen, _close
    
    while not _close:
        _screen.fill(display.BLACK)
        _clock.tick(60) # Se establecen el frame rate (fps)
        if platform.system() != "Windows":
            buttons = []
            display.show_msg(_screen, "Este Programa solo funciona en Windows")
        else:
            buttons = display.showOptions(_screen)  
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                _close = True
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

def start_excel_activity(private_key:RSAPrivateKey=None):
    global _screen, _close, _screen
    
    if not os.path.exists(excel.get_excel_path()):
        raise Exception("No existe el fichero patients_data.xlsx en la carpeta .data")
    if excel.empty() and private_key is None:
        raise Exception("El archivo patients_data.xlsx esta vacio, csv editor no permitido")
    
    public_key = load_pem_public_key(config.get("public_key_path"))
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
            sensitive_fields=config.get('sensitive_fields')
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
    else:
        open_csveditor()
    excel.update_excel()
    # Cerramos el programa
    _close = True
        
def ask_private_key() -> tuple[bool, Union[RSAPrivateKey, None]]:
    global _screen, _close, _screen
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
                try:
                    private_key = load_pem_private_key(key_file_path, password=password.encode())
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






