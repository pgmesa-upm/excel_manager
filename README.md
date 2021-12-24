
# EXCEL MANAGER (V-1.0) (solo compatible con Windows)

### Autor
Pablo García Mesa
- pgmesa.sm@gmail.com
- https://github.com/pgmesa-upm/excel_manager

### 0. Descripción
Programa para el manejo del excel del estudio de esclerosis múltiple, llevado a cabo por la UPM en colaboración con el oftalmológico del Gregorio Marañón 

### 1. Modo de uso
El programa necesita Python (>=3.9) para ejecutarse, por lo que en el disco duro debe haber una carpeta '.python' que contenga el python ('.python/Python39') necesario con los módulos requeridos para ejecutar el programa. 

El programa se abre ejecutando el archivo '.bat' que se encuentra en la carpeta root del programa. Este necesita de la carpeta'.python' antes mencionada. En caso de no existir, se puede ejecutar el programa con un intérprete de python en el ordenador en cuestión que tenga todos los módulos requeridos instalados (mirar requirements.txt)

Al ejecutar el programa se abrirán: una terminal (ignorar y no cerrar nunca, se cierra sola al final) y una interfaz que en la que el usuario puede elegir en que modo registrarse:
- Modo Usuario:
    Este modo está pensado para que solo se pueda añadir información al excel, pero no se puede modificar la existente, por lo que hay que tener cuidado y estar seguro de lo que se añade es correcto, porque una vez guardado no se podrá volver a editar es información desde el modo usuario. Al pinchar en el modo usuario se abrirá SIEMPRE el csv_editor con 5 filas para añadir información (si se quiere añadir más, con guardar la información se volverán a tener las 5 filas en blanco). aparecerán los headers definidos por los administradores y las filas en blanco para añadir nuevos datos. Puede que el proceso de encriptación de datos tarde un poco al guardar los datos. 
    Para ver el feedback del csv editor siempre hay que mirar el título de la ventana. En este también aparecen el número de filas que tiene el excel, (por ejemplo, para que el user sepa cuál es número del paciente nuevo que está introduciendo). En el menu se mostrarán las distantias hojas de excel que se pueden editar
- Modo Administrador:
    Este modo permite la edición completa del excel desencriptado. Tanto desde el excel como desde el csv-editor (muy limitado actualmente este último). Primero se abrirá un explorador de archivos (puede tardar un poco en cargar), en el que se debe seleccionar la clave privada que se ha generado para el estudio, a continuación se debe introducir la contraseña con la que se serializo esta clave privada. Si las credenciales son correctas se abrirá el editor que este como predeterminado. Si son incorrectos y sabe que la contraseña es correcta, puede que haya seleccionado el archivo que no es, por lo que para seleccionar otro archivo cierre el programa y ábralo de nuevo. ¡El excel puede que se habrá sin ningún formato establecido o pierda el que tenía!

Todas las veces que se edite tanto en modo usuario como en modo admin, se guardara una copia de backup del excel antes de la edición, en la carpeta '.data/.backup' con la fecha y hora de la edición de dicho archivo.

En la carpeta .config se encuentra el fichero config.json el cual permite modificar algunos parámetros del script:
- "excel_path": No tocar, no se encuentra habilitado

- "admin_editor_preference": Elegir entre "excel" o "csv". Se recomienda dejarlo en excel por defecto, aunque si no se encuentra excel en el ordenador (saltará un mensaje de error de windows), se abrirá el csv_editor. El csv editor se encuentra en fase de desarrollo, y aunque es funcional y permite editar información en modo administrador, la interfaz todavía tiene bastantes bugs y no es cómodo trabajar con este (mirar apartado de csv_editor para más información) (El csv-editor del modo user funciona perfectamente)

- "public_key_path": Permite definir la ruta relativa (tomando la carpeta del programa como base) o ruta absoluta del fichero que contiene la clave pública. Se recomienda no tocar este parámetro y dejar siempre el fichero de la clave publica en la ruta predeterminada '.config/public_key' para que otros usuarios lo puedan utilizar también.

- "orientation": "colums" o "rows". No se encuentra habilitada la opción de rows actualmente.

- "sensitive_fields": Es una lista en la que se especifican los campos que contienen información sensible y los cuales serán encriptados (tanto en modo user como modo admin si se introducen cambios) y desencriptados (en modo admin)

Todo el programa depende de un archivo excel que se debe colocar en la carpeta .data con el nombre 'patients_data.xlsx' (en un futuro se podrá elegir). Este excel se debe tratar como una única tabla en la que cada columna debe tener un header correspondiente. No debería haber datos fuera de la tabla sin un header correspondiente o anotaciones en celdas fuera de la tabla (se debe tratar como un csv). Además esta tabla debe empezar desde la primera celda (1,A) y no contener filas en blanco de márgenes (si se ponen estas se verán reflejadas en el editor y no se cogerán bien los headers). 
!!Si no se siguen estas indicaciones puede que surja algún error en el programa y el excel se acabe escribiendo mal
y se pierda la información¡¡
El csv_editor no se podrá abrir a menos que el excel no este vacío, es decir, que contenga al menos dos filas, una con los headers de la tabla y otra con un primer dato introducido en la columna (con un solo dato en la columna vale)
- Ej de excel no vacío: 
    ```
    Nombre Apellido Genero
    Felipe            M     
    ```  

Puede que los tipos no se almacenen correctamente en el excel (números se pueden guardar como strings)(Se deja así para evitar problemas con algún tipo de expresiones que pueden ser interpretadas erróneamente como formulas)
Excel te avisa luego si quieres que lo interprete como numero o dejarlo así 

config.json:
admin_editor_preference(solo para modo administrador): "csv" o "excel"(recomendado)
no tocar excel_path aun no funcional y orientation tampoco funcional

El explorador de archivos tarda un poco en salir

No cerrar el programa con el excel abierto (el programa de todas formas intentara impedir su cierre si detecta
que el excel está en modo edición (si no se activa modo edición no se detectara como que se está editando y se podra cerrar el programa impidiendo encriptar la información sensible))

Todo lo almacenado en '.data/.protected_data' queda guardado y aunque se elimine el paciente la información seguira ahi. Está hecho para permitir que las versiones de backup sigan teniendo acceso a la info encriptada

### 2. Resumen para instalar el programa en un disco duro
- Descargar el repositorio del programa de github en la carpeta root del disco
- Poner el excel que contiene la información en la carpeta '.data/' y renombrarlo a patients_data.xlsx
- Poner la public_key en '.config/' o especificar en config.json su ruta
- Crear el archivo config.json (copie la info de default_config.json) y modificar lo necesario para el proyecto
    en cuestión
- Ejecutar la aplicación y ver que funciona (se guardara un backup del excel sin encriptar, bórrelo en caso
    de que no quiera conservar ese fichero sin la encriptación [solo se hace la primera vez que se abre el excel antes de encriptar, si ya está encriptado se hace siempre el backup del excel encriptado])

### 3. Errores y como solucionarlos
- 'IndexError: At least one sheet must be visible' se debe a que el excel tiene un formato incorrecto al
    mencionado anteriormente y ha habido un problema al querer actualizar las hojas csv en el excel. Ahora el fichero, como puedes comprobar, no se habre, debido a que se ha escrito mal sobre él y no es reconocido por excel. Este es un caso de pérdida de informacion del documento, pero deberia haber una copia de seguridad en '.data/.backups' de archivo perdido. De todas formas, siempre se recomienda la primera vez que se usa el programa, guardar una copia del archivo original por si la primera vez no funciona y hay algo del excel que no tiene el formato correcto. Una vez funciona la primera vez, es seguro que funcionara de aqui en adelante si solo se modifica el excel a traves de la aplicacion. 

### 4. CSV-editor
En el menú se mostrarán las distintas hojas de excel que se pueden editar y algunas otras funcionalidades (por ahora solo guardar). Los atajos de teclado como ctrl-s, ctrl-v y demas, están implementados.
Siempre mirar al título de la ventana del editor para obtener feedback del programa. 
- Para el modo usuario:
    Se encuentra totalmente funcional. Siempre 5 filas para añadir información y cuando se guardan cambios se vuelven a poner en blanco. Al cambiar de una hoja a otra solo cambia el titulo (parece que no ha hecho nada pero sí)
- Para el modo administrador:
    Es muy limitado actualmente, aunque realiza todas las funciones de forma correcta, se puede editar con el confiando en que todo se almacenara y encriptara bien. El problema es la interfaz, que tiene bugs y no es como de trabajar con ella:
    Se descuadran las tablas al cambiar entre hojas y no se pueden añadir nuevas filas a la tabla para añadir nuevos campos. 

- Limitaciones y cosas a tener en cuenta:

### 5. Futuros cambios y modificaciones sugeridos a arreglar
#### CSV-editor:
- Corregir bug al cambiar entre hojas csv con distinto tamaño
- El canvas se ve desbordado por las celdas
- La rueda del raton no funciona para moverse por la tabla 
- Mejora de las scrollbar en general con los atajos de teclado
#### Config:
- Habilitar las opciones que actualmente no están funcionales (sobre todo el que el nombre del fichero excel sea el que quieras y pueda estar donde quieras [fácil de implementar])
#### Ideas:
- Añadir un campo a config.json que indique que campo se toma como identificador de la fila y que el programa solo vaya autoincementando el número de patient Ej: "id_field": {name: "PATIENT_NUM", "expression": "patient_"}
