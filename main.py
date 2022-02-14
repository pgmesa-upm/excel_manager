
import os
import sys

try:
    import GUI.views as views
except ModuleNotFoundError as err:
    print("[!] ERROR: No se han instalado todas las dependencias del programa",
          f"\n -> ERROR_MSG: {err}",
          "\n -> Introduce 'pip install -r requirements.txt', a ser posible en un entorno virtual aislado")
    exit(1)

# ----------------------------------------------------------------------
# Programa creado por el alumno Pablo García Mesa para la interaccion 
# con el Excel de la investigación de Esclerosis Multiple, RIS y NMO, 
# llevada a cabo en el oftalmológico del GM y realizado en conjunto con 
# la UPM.
# ----------------------------------------------------------------------

# -- Python version check ---
dig1, dig2 = sys.version.split('.')[:2]
req_d1, req_d2 = 3, 9
print(f"Detected python version: {dig1}.{dig2}")
print(f"Required python version: {req_d1}.{req_d2} or higher")
if req_d1 > int(dig1) or req_d2 > int(dig2):
    print(f"ERROR: The python version must be {req_d1}.{req_d2} or higher")
    exit(1)
# ---------------------------

# INICIO DEL PROGRAMA (Esquema basico de funcionamiento)
def main():
    print(os.getcwd())
    views.init()
    while not views._close:
        try:
            mode = views.select_mode()
            if mode == views.USER_MODE:
                views.start_excel_activity()
            elif mode == views.ADMIN_MODE:
                correct_key, private_key = views.ask_private_key()
                if correct_key:
                    views.start_excel_activity(private_key=private_key)
        except PermissionError:
            views.error("PERMISSION ERROR: El excel ya estaba abierto o siendo usado por un tercero")
        except Exception as err:
            views.error(str(err))
    views.close()
    
if __name__ == "__main__":
    main()