
# Programa para el manejo del excel del estudio (V-1.0) (solo compatible con Windows)

1. Modo de uso:
El programa necesita Python (>=3.9) para ejecutarse, por lo que en el disco duro se encuentra una carpeta '.python' que contiene el python necesario con los modulos requerido para ejecutar el programa (no tocar)
El programa se almacena el la carpeta 'excel_program' en la carpeta root del disco duro.

El programa se abre ejecutando el data_editor.bat que se encuentra en la carpeta root del disco duro.
Se abriran: una terminal (ignorar y no cerrar nunca, se cierra sola al final) y una interfaz que en la que el usuario puede elegir en que modo registrarse:
- Modo Usuario:
    Este modo esta pensado para que solo se pueda añadir informacion al excel, pero no se puede modificar la existente, por lo que hay que tener cuidado y estar seguro de lo que se añade es correcto, porque una vez guardado no se podra volver a editar es informacion desde el modo usuario. Al pinchar en el modo usuario se abrira SIEMPRE el csv_editor con 5 filas para añadir informacion (si se quiere añadir mas, con guardar la informacion se volveran a tener las 5 filas en blanco). Apareceran los headers definidos por los administradores y las filas en blanco para añadir nuevos datos. Puede que el proceso de encriptacion de datos tarde un poco al guardar los datos. 
    Para ver el feedback del csv editor siempre hay que mirar el titulo de la ventana. En este tambien aparecen el numero de filas que tiene el excel, (por ejemplo para que el user sepa cual es numero del paciente nuevo que esta introduciendo). En el menu se mostraran las distantias hojas de excel que se pueden editar
- Modo Administrador:
    Este modo permite la edicion completa del excel desencriptado. Tanto desde el excel como desde el csv-editor (muy limitado actualmente este ultimo). Primero se abrira un explorador de archivos (puede tardar un poco en cargar), en el que se debe seleccionar la clave privada que se ha generado para el estudio, a continuacion se debe introducir la contraseña con la que se serializo esta clave privada. Si los credenciales son correctos se abrira el editor que este como predeterminado. Si son incorrectos y sabe que la contraseña es correcta, puede que haya seleccionado el archivo que no es, por lo que para seleccionar otro archivo cierre el programa y abralo de nuevo. ¡El excel puede que se habra sin ningun formato establecido o pierda el que tenia!

Todas las veces que se edite tanto en modo usuario como en modo admin, se guardara una copia de backup del excel anted de la edicion, en la carpeta '.data/.backup' con la fecha y hora de la edicion de dicho archivo.

En la carpeta .config se encuentra el fichero config.json el cual permite modificar algunos parametros del script:
- "excel_path": No tocar, no se enceuntra habilitado

- "admin_editor_preference": Elegir entre "excel" o "csv". Se recomienda dejarlo en excel por defecto, aunque si no se encuentra excel en el ordenador (saltara un mensaje de error de windows), se abrira el csv_editor. El csv editor se encuentra en fase de desarrollo, y aunque es funcional y permite editar informacion en modo administrador, la interfaz todavía tiene bastantes bugs y no es comodo trabajar con este (mirar apartado de csv_editor para mas informacion) (El csv-editor del modo user funciona perfectamente)

- "public_key_path": Permite definir la ruta relativa (tomando la carpeta del programa como base) o ruta absoluta del fichero que contiene la clave publica. Se recomienda no tocar este parametro y dejar siempre el fichero de la clave publica en la ruta predeterminada '.config/public_key' para que otros usuarios lo puedan utilizar tambien.

- "orientation": "colums" o "rows". No se encuentra habilitada la opcion de rows actualmente.

- "sensitive_fields": Es una lista en la que se especifican los campos que contienen informacion sensible y los cuales seran encriptados (tanto en modo user como modo admin si se introducen cambios) y desencriptados (en modo admin)

Todo el programa depende de un archivo excel que se debe colocar en la carpeta .data con el nombre 'patients_data.xlsx' (en un futuro se podra elegir). Este excel se debe tratar como una unica tabla en la que cada columna debe tener un header correspondiente. No deberia haber datos fuera de la tabla sin un header correspondiente o anotaciones en celdas fuera de la tabla (se debe tratar como un csv). Ademas esta tabla debe empezar desde la primera celda (1,A) y no contener filas en blanco de margenes (si se ponen estas se veran reflejadas en el editor y no se cogeran bien los headers). 
!!Si no se siguen estas indicaciones puede que surja algun error en el programa y el excel se acabe escribiendo mal
y se pierda la informacion¡¡
El csv_editor no se podra abrir a menos que el excel no este vacio, es decir, que contenga al menos dos filas, una con los headers de la tabla y otra con un primer dato introducido en la columna (con un solo dato en la columna vale)
-> Ej de excel no vacio: 
    Nombre Apellido Genero
    Felipe            M       

Puede que los tipos no se almacenen correctamente en el excel (numeros se pueden guardar como strings)(Se deja asi para evitar porblemas con algun tipo de expresiones que pueden ser interpretadas erroneamente como formulas)
Excel te avisa luego si quieres que lo interprete como numero o dejarlo asi 

config.json:
admin_editor_preference(solo para modo administrador): "csv" o "excel"(recomendado)
no tocar excel_path aun no funcional y orientation tampoco funcional

El explorador de archivos tarda un poco en salir

No cerrar el programa con el excel abierto (el programa de todas formas intentara impedir su cierre si detecta
que el excel esta en modo edicion (si no se activa modo edicion no se detectara como que se esta editando y se podra cerrar el programa impidiendo encriptar la informacion sensible))

Todo lo almacenado en '.data/.protected_data' queda guardado y aunque se elimine el paciente la informacion seguira ahi. Esta hecho para permitir que las versiones de backup sigan teniendo acceso a la info encriptada

2. Resumen para instalar el programa en un disco duro
    - Descargar el repositorio del programa de github en la carpeta root del disco
    - Poner el excel que contiene la informacion en la carpeta '.data/' y renombrarlo a patients_data.xlsx
    - Poner la public_key en '.config/' o especificar en config.json su ruta
    - Crear el archivo config.json (copie la info de default_config.json) y modificar lo necesario para el proyecto
        en cuestion
    - Ejecutar la aplicacion y ver que funciona (se guardara un backup del excel sin encriptar, borrelo en caso
        de que no quiera conservar ese fichero sin la encriptacion [solo se hace la primera vez que se abre el excel antes de encriptar, si ya esta encriptado se hace siempre el backup del excel encriptado])

3. Errores y como solucionarlos:
    - 'IndexError: At least one sheet must be visible' se debe a que el excel tiene un formato incorrecto al
        mencionado anteriormente y ha habido un problema al querer actualizar las hojas csv en el excel. Ahora el fichero, como puedes comprobar, no se habre, debido a que se ha escrito mal sobre el y no es reconocido por excel. Este es un caso de perdida de informacion del documento, pero deberia haber una copia de seguridad en '.data/.backups' de archivo perdido. De todas formas siempre se recomienda la primera vez que se usa el programa, guardar una copia del archivo original por si la primera vez no funciona y hay algo del excel que no tiene el formato correcto. Una vez funciona la primera vez, es seguro que funcionara de aqui en adelante si solo se modifica el excel a traves de la aplicacion. 

3. CSV-editor:
En el menu se mostraran las distantias hojas de excel que se pueden editar y algunas otras funcionalidades (por ahora solo guardar). Los atajos de teclado como ctrl-s, ctrl-v y demas, estan implementados.
Siempre mirar al titulo de la ventan del editor para obtener feedback del programa. 
Cuando se guardan los camb
- Para el modo usuario:
    Se encuentra totalmente funcional. Siempre 5 filas para añadir informacion y cuando se guardan cambios se vuelven a poner en blanco. Al cambiar de una hoja a otra solo cambia el titulo (parece que no ha hecho nada pero si)
- Para el modo administrador:
    Es muy limitado actualmente, aunque realiza todas las funciones de forma correcta, se puede editar con el confiando en que todo se almacenara y encriptara bien. El problema es la interfaz, que tiene bugs y no es como de trabajar con ella:
    Se descuadran las tablas al cambiar entre hojas y no se pueden añadir nuevas filas a la tabla para añadir nuevos campos. 

- Limitaciones y cosas a tener en cuenta:

4. Futuros cambios y modificaciones sugeridos a arreglar:
-> CSV-editor:
    - Corregir bug al cambiar entre hojas csv con distinto tamaño
    - El canvas se ve desbordado por las celdas
    - La rueda del raton no funciona para moverse por la tabla 
    - Mejora de las scrollbar en general con los atajos de teclado
-> Config:
    - Habilitar las opciones que actualmente no estan funcionales (sobre todo el que el nombre del fichero excel sea
        el que quieras y pueda estar donde quieras [facil de implementar])
-> Ideas:
    - Añadir un campo a config.json que indique que campo se toma como identificador de la fila
    y que el programa solo vaya autoincementando el numero de patient
    Ej: "id_field": {name: "PATIENT_NUM", "expression": "patient_"}
