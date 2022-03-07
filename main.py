# -- Encoding UTF-8 -- #
import os
import sys
from pathlib import Path

# ----------------------------------------------------------------------
# Programa creado para la interaccion con el Excel de la investigación
# de Esclerosis Multiple, RIS y NMO, llevada a cabo en el oftalmológico
# del Gregorio Marañón y en conjunto con la UPM.
#
# @autor: Pablo García Mesa
# ----------------------------------------------------------------------

try:
    from login import get_login_info, init_login
    import GUI.views as views
    from crypt_utilities.asymmetric import generate_rsa_key_pairs
    from config import get
    from editor.protected_data import hashed_ids_file_path
except ModuleNotFoundError as err:
    print("[!] ERROR: No se han instalado todas las dependencias del programa",
          f"\n -> ERROR_MSG: {err}",
          "\n -> Introduce 'pip install -r requirements.txt', a ser posible en un entorno virtual aislado")
    exit(1)

# -- Python version check ---
dig1, dig2 = sys.version.split('.')[:2]
req_d1, req_d2 = 3, 9
print(f"Detected python version: {dig1}.{dig2}")
print(f"Required python version: {req_d1}.{req_d2} or higher")
if req_d1 > int(dig1) or req_d2 > int(dig2):
    print(f"ERROR: The python version must be {req_d1}.{req_d2} or higher")
    exit(1)
# ---------------------------

program_path = Path(__file__).parent.resolve()
public_key_path_str = get('public_key_path')
if public_key_path_str != None:
    public_key_path = Path(public_key_path_str)
    if not public_key_path.is_absolute():
        public_key_path = program_path/public_key_path_str

# INICIO DEL PROGRAMA (Esquema basico de funcionamiento)
def main():
    print("Program Location:", program_path)
    hashed_pw, _ = get_login_info()
    if hashed_pw is None:
        if os.path.exists(hashed_ids_file_path):
            print("[!] No se ha encontrado ninguna contraseña de acceso para el programa")
            print("¿Desea añadir una?")
            print("Se perderan todos los datos de /.data/.hashed_ids (buscar por id en el modo usuario dejará de funcionar para los datos encriptados)")
            print("Hará falta que un administrador abra el excel para refrescar el archivo")
            answer = str(input("=> Respuesta (y/n): "))
            if answer.lower() != 'y':
                print("[!] Operation cancelled (you must recover the /.data/.login file to run the program)")
                exit(1)
        init_login()
    if not os.path.exists(public_key_path):
        print(f"The program didn't find a public_key in '{public_key_path}'")
        answer = str(input("=> Do you want to create an rsa-key-pair now? (y/n): "))
        if answer.lower() != "y":
            print("[!] Operation cancelled")
        else:
            generate_rsa_keys()
    views.init()
    outcome = views.login()
    while not views._close:
        if outcome == 0:
            try:
                mode = views.select_mode()
                if mode == views.USER_MODE:
                    while True:
                        action = views.select_user_action()
                        if action == 'add':
                            views.start_editor()
                        elif action == 'check':
                            views.check_id()
                        elif action is None:
                            break
                elif mode == views.ADMIN_MODE:
                    correct_key, private_key = views.ask_private_key()
                    if correct_key:
                        views.start_editor(private_key=private_key)
                elif mode is None:
                    views._close = True
            except PermissionError:
                views.error("PERMISSION ERROR: El excel ya estaba abierto o siendo usado por un tercero")
            except Exception as err:
                views.error(str(err))
        else:
            views._close = True
    views.close()

def generate_rsa_keys():
    print(f"[%] Keys will be stored in '{public_key_path.parent}'")
    if os.path.exists(public_key_path):
        print(f"The program found a public_key in '{public_key_path}'")
        answer = str(input("=> Do you want to override it? (y/n): "))
        if answer.lower() != "y":
            print("[!] Operation cancelled")
            exit()
    serialization_key = str(input("+ Introduce the password for your private_key (void if don't want to add it): "))
    if serialization_key == "": serialization_key = None
    generate_rsa_key_pairs(private_key_password=serialization_key, quiet=False, file_path=public_key_path.parent)
    print(f"=> RSA-keys are located in '{public_key_path.parent}'")
    print("[%] Remember to don't leave the private_key file in the project")

if __name__ == "__main__":
    try:
        if "--gen-rsa-key-pair" in sys.argv:
            generate_rsa_keys()
        else:
            main()
    except KeyboardInterrupt:
        print("[%] Exiting...")
        exit(1)
    except Exception as err:
        print(f"[!] Error: {err}")
        exit(1)