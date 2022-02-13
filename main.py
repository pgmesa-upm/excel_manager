
import os
import GUI.views as views

# ----------------------------------------------------------------------
# Programa creado para la interaccion con el Excel de la investigación
# de Esclerosis Multiple, RIS y NMO, llevada a cabo en el oftalmológico
# del GM y realizado en conjunto con la UPM.
# ----------------------------------------------------------------------

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
        except Exception as err:
            views.error(str(err))
    views.close()
    
if __name__ == "__main__":
    main()