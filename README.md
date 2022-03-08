
# EXCEL MANAGER (V-3.0) (solo compatible con Windows)

### Autor
Pablo García Mesa
- pgmesa.sm@gmail.com
- https://github.com/pgmesa-upm/excel_manager

### 0. Descripción
Programa para el manejo del excel del estudio de esclerosis múltiple, llevado a cabo por la UPM en colaboración con el oftalmológico del Gregorio Marañón

### 1. Modo de uso
El programa necesita Python (>=3.9) para ejecutarse, por lo que en el disco duro debe haber una carpeta '.python' que contenga el python ('.python/Python39') necesario con los módulos requeridos para ejecutar el programa. 

El programa se abre ejecutando el archivo '.bat' que se encuentra en la carpeta root del programa. Este necesita de la carpeta'.python' antes mencionada. En caso de no existir, se puede ejecutar el programa con un intérprete de python en el ordenador en cuestión que tenga todos los módulos requeridos instalados (mirar requirements.txt)
```
pip install -r requirements.txt
```
Al ejecutar el programa se abrirán: una terminal por donde aparecen los logs del programa y por donde se deben realizar unas primeras configuraciones la primera vez que se ejecuta (generación de claves y credenciales para el programa) (no cerrar nunca directamente mientras la interfaz del programa siga abierta) y una interfaz que en la que el usuario puede elegir en que modo registrarse.
#### Generación de Claves y Credenciales
La primera vez que se ejecute el programa se pedirá por consola una contraseña con la que se restringirá el accesso a todos aquellos que no deban usar el programa (el programa utiliza esta contraseña internamente también para otras finalidades). En caso que no se encuentre la clave pública en el sitio especificado en la configuración '.config.json', se le preguntará si quiere generar un nuevo par de claves RSA en esa ubicación. Recuerde guardar la clave privada 'private_key' en un lugar seguro (esta clave privada es lo que distingue a un administrador de un usuario). 
#### Niveles de Uso
- **Modo Usuario**:

    Este modo está pensado para que solo se pueda añadir información al excel, pero no se puede modificar la existente, por lo que hay que tener cuidado y estar seguro de lo que se añade es correcto, porque una vez guardado no se podrá volver a editar es información desde el modo usuario. Al pinchar en el modo usuario se abrirá SIEMPRE el csv_editor con 5 filas para añadir información (si se quiere añadir más, con guardar la información se volverán a tener las 5 filas en blanco). Aparecerán los headers definidos por los administradores y las filas en blanco para añadir nuevos datos. Puede que el proceso de encriptación de datos tarde un poco al guardar los datos (no interrumpir este proceso).
    Para ver el feedback del csv editor siempre hay que mirar el título de la ventana. En este también aparecen el número de filas que tiene el excel. En el menu se mostrarán las distintas hojas de excel que se pueden editar. Al poner un excel nuevo, este no se encriptará hasta que un administrador entre con credenciales, guarde el excel y cierre el programa. 
- **Modo Administrador**:

    Este modo permite la edición completa del excel desencriptado. Tanto desde el excel como desde el csv-editor (muy limitado actualmente este último). Primero se abrirá un explorador de archivos (puede tardar un poco en cargar), en el que se debe seleccionar la clave privada que se ha generado para el estudio, a continuación se debe introducir la contraseña con la que se serializó esta clave privada. Si las credenciales son correctas se abrirá el editor que esté como predeterminado. Si son incorrectos y sabe que la contraseña es correcta, puede que haya seleccionado el archivo que no es, por lo que para seleccionar otro archivo cierre el programa y ábralo de nuevo.
    Se ha conseguido implementar que el excel no pierda el formato al leer/escribir sobre él (no simpre se mantiene todo a la perfección, colores, negritas etc...) 

[INFO]
Siempre que se modifique algún parámetro de la configuración, se debe entrar con el modo administrador y cerrar el programa para refrescar la información (nuevos campos a encriptar o cualquier otro cambio en la configuración) antes de que cualquier usuario intente añadir nada.

Todas las veces que se edite tanto en modo usuario como en modo admin, se guardará una copia de backup del excel antes de la edición, en la carpeta '.data/.backup' con la fecha y hora de la edición de dicho archivo. Por tanto, la primera vez que se encripte, primero se guardará tal y como estaba, por lo que debería eliminarse manualmente este primer archivo ya que contiene los datos sin desencriptar. Esto se hace así por si ocurre algún fallo inesperado, que no se pierda la información del archivo. Los directorios de backup de archivos sin encriptar aparecerán con un 'NP-' al inicio de su nombre ('not-protected'). Si no se quiere que se haga backup de los excel con datos sin encriptar se debe dajar a 'false' el campo 'backup-not-encrypted' en el fichero de configuración.

Para recuperar un backup, eliminar el excel actual y el archivo .protected_data y copiar los archivos del directorio a recuperar en la carpeta './data'. Por último, renombre el archivo excel con el nombre que haya especificado en la configuración

En la carpeta .config se encuentra el fichero config.json el cual permite modificar algunos parámetros del script:
- "excel_path": path donde se encontrara el archivo por defecto '.data/patients_data.xlsx'

- "admin_editor_preference": Elegir entre "excel" o "csv". Se recomienda dejarlo en excel por defecto, aunque si no se encuentra excel en el ordenador (saltará un mensaje de error de windows), se abrirá el csv_editor. El csv editor se encuentra en fase de desarrollo, y aunque es funcional y permite editar información en modo administrador, la interfaz todavía tiene bastantes bugs y no es cómodo trabajar con este (mirar apartado de csv_editor para más información) (El csv-editor del modo user funciona perfectamente)

- "public_key_path": Permite definir la ruta relativa (tomando la carpeta del programa como base) o ruta absoluta del fichero que contiene la clave pública. Se recomienda no tocar este parámetro y dejar siempre el fichero de la clave publica en la ruta predeterminada '.config/public_key' para que otros usuarios lo puedan utilizar también.

- "date_format": Formato en el que guardar las fechas en el excel. "%d/%m/%Y" por defecto

- "orientation": "colums" o "rows". No se encuentra habilitada la opción de rows actualmente.

- "id_field": String que indica el campo identificador de cada fila. Permite a un usuario saber si un identificador dado ya se encuentra registrado en el excel, para no añadirlo 2 veces.

- "sensitive_fields": Es una lista en la que se especifican los campos que contienen información sensible y los cuales serán encriptados (tanto en modo user como modo admin si se introducen cambios) y desencriptados (en modo admin)

- "data_types": Es un objeto JSON ({}) cuyos atributos dentro serán los campos asociados con un tipo de dato para la columna. Datos válidos -> 'str', 'str-q', 'date', 'int', 'float'. 'str-q' añade una comilla simple al valor del campo para impedir que excel lo detecte como una formula incorrectamente (-2.5/+2.5 | excel interpreta: -1 -> '-1.2/+2.5 | excel interpreta: -1.2/+2.5)

- "hide_fields_from_users": Es una lista. Los campos que se introduzcan aquí, no apareceran en el csv editor cuando un usuario vaya a introducir información nueva (luego los admin se ocuparán de rellenar esa información)

- "backup-not-encrypted": Bool. Permite o evita que se hagan backups de excels no encriptados

Ejemplo de config.json
```
{
    "excel_path": "./.data/patients_data.xlsx",
    "admin_editor_preference": "excel", 
    "public_key_path": "./.config/public_key",
    "date_format": "%d/%m/%Y",
    "orientation": "colums",
    "id_field": "NHC",
    "sensitive_fields": ["NHC", "LAST_NAME", "FIRST_NAME", "BIRTH_DATE"],
    "data_types": {
        "STUDY_NUM": "int",
        "PATIENT_NUM": "int",
        "NHC": "int",
        "LAST_NAME": "str",
        "FIRST_NAME": "str",
        "SEX": "str",
        "BIRTH_DATE": "date",
        "STUDY_DATE": "date",
        "OD_DIOPTERS": "str-q",
        "OS_DIOPTERS": "str-q",
        "VISUAL_ACUITY": "str-q"
    },
    "hide_fields_from_users": ["STUDY_NUM", "PATIENT_NUM"],
    "backup-not-encrypted": false
}
```
Todo el programa depende del archivo excel. Este excel se debe tratar como una única tabla en la que cada columna debe tener un header correspondiente. No debería haber datos fuera de la tabla sin un header correspondiente o anotaciones en celdas fuera de la tabla (se debe tratar como un csv) (no se recomienda poner fórmulas). Además esta tabla debe empezar desde la primera celda (1,A) y no contener filas en blanco de márgenes (si se ponen estas se verán reflejadas en el editor y no se cogerán bien los headers). Se pueden tener las hojas que se quieran pero todas deberían tener los mismos headers.
¡¡Si no se siguen estas indicaciones puede que surja algún error en el programa y el excel se acabe escribiendo mal
y se pierda la información!! (Para evitar esto, es por lo que el programa realiza de forma automática el backup antes de tocar el archivo)
El csv_editor no se podrá abrir a menos que el excel no este vacío, es decir, que contenga al menos dos filas, una con los headers de la tabla y otra con un primer dato introducido en la columna (con un solo dato en la columna vale)
- Ej de excel no vacío: 
    ```
    Nombre Apellido Genero
    Felipe            M     
    ```  

Puede que los tipos no se almacenen correctamente en el excel (números se pueden guardar como strings) (Se deja así para evitar problemas con algún tipo de expresiones que pueden ser interpretadas erróneamente como formulas)
Excel te avisa luego si quieres que lo interprete como numero o dejarlo así. Si se introduce un tipo de dato que no corresponde al asignado, se guardará como un string

No cerrar el programa con el excel abierto (el programa de todas formas intentara impedir su cierre si detecta
que el excel está en modo edición (si no se activa modo edición no se detectará como que se está editando y se podrá cerrar el programa impidiendo encriptar la información sensible))

### 2. Resumen para instalar el programa en un disco duro
- Descargar el repositorio del programa de github en el disco
- Poner el excel que contiene la información en la carpeta '.data/' y renombrarlo a patients_data.xlsx o actualizar el excel_path de 'config.json'
- Crear el archivo config.json (copie la info de default_config.json) y modificar lo necesario para el proyecto en cuestión
- Ejecutar el programa y generar las contraseñas necesarias (la de inicio y el par de claves RSA si no se tiene ya alguna que se quiera usar)
- Poner la 'public_key' en '.config/' o especificar en config.json su ruta y poner en un sitio seguro la 'private_key'
- Ejecutar la aplicación y ver que funciona (se guardará un backup del excel sin encriptar, bórrelo en caso de que no quiera conservar ese fichero sin la encriptación [solo se hace la primera vez que se abre el excel antes de encriptar, si ya está encriptado se hace siempre el backup del excel encriptado]. Ponga a 'false' la variable 'backup-not-encrypted' en el fichero de configuración para evitar que se relize el backup del excel sin encriptar)
- Entrar con el modo administrador, guardar el excel y salir del programa para que se encripten todos los campos especificados en la configuración

### 3. Errores y como solucionarlos
- 'IndexError: At least one sheet must be visible' se debe a que el excel tiene un formato incorrecto al
    mencionado anteriormente y ha habido un problema al querer actualizar las hojas csv en el excel. Ahora el fichero, como puedes comprobar, no se abre, debido a que se ha escrito mal sobre él y no es reconocido por excel. Este es un caso de pérdida de informacion del documento, pero debería haber una copia de seguridad en '.data/.backups' del archivo perdido. De todas formas, siempre se recomienda la primera vez que se usa el programa, guardar una copia del archivo original por si la primera vez no funciona y hay algo del excel que no tiene el formato correcto. Una vez funciona la primera vez, es seguro que funcionará de aquí en adelante si solo se modifica el excel a través de la aplicación. 
- Puede que usando el csv editor, si se tarda mucho en guardar los cambios, el disco duro se duerma y al querer guardar los cambios se produzca un error. Para solucionarlo, si se ve la luz del disco apagada, hay que meterse desde el explorador de archivos en alguna de sus carpetas para despertarlo. Una vez despertado (luz azul encendida) ya se puede proceder a guardar los cambios con normalidad.

### 4. CSV-editor
En el menú se mostrarán las distintas hojas de excel que se pueden editar y algunas otras funcionalidades (por ahora solo guardar). Los atajos de teclado como ctrl-s, ctrl-v y demás, están implementados.
Siempre mirar al título de la ventana del editor para obtener feedback del programa. 
- Para el modo usuario:
    Se encuentra totalmente funcional. Siempre 5 filas para añadir información y cuando se guardan cambios se vuelven a poner en blanco. Al cambiar de una hoja a otra solo cambia el título (parece que no ha hecho nada pero sí)
- Para el modo administrador:
    Es muy limitado actualmente, aunque realiza todas las funciones de forma correcta, se puede editar con él confiando en que todo se almacenará y encriptará bien. El problema es la interfaz, que tiene bugs y no es cómodo trabajar con ella: Se descuadran las tablas al cambiar entre hojas y no se pueden añadir nuevas filas a la tabla para añadir nuevos campos. 

### 5. Futuros cambios y modificaciones sugeridos a arreglar
#### CSV-editor:
- Corregir bug al cambiar entre hojas csv con distinto tamaño
- El canvas se ve desbordado por las celdas en el modo administrador
- La rueda del ratón no funciona para moverse por la tabla 
- Mejora de las scrollbar en general con los atajos de teclado
#### Config:
- Habilitar las opciones que actualmente no están funcionales ('orientation')

### 6. Comandos adicionales:
Si ejecuta:
```
python main.py --gen-rsa-key-pair
```
Se volverán a generar las claves pública y privada donde esté indicdo en el archivo de configuración.

## Lectura complementaria sobre el funcionamiento del programa (información no necesaria para utilizar el programa)
### 6. Método de encriptación de los datos
Este programa utiliza una librería llamada 'crypt_utilities', desarrollada también por el autor de este programa, que se basa en la conocida libreria criptográfica de 'cryptography'. Este programa utiliza encriptación asimétrica RSA (clave pública:encripta - clave privada:desencripta).

Para desencriptar los campos es necesario por tanto, el fichero con clave privada y la contraseña con la que se serializó la contraseña (si es que se utilizó alguna). El fichero de acceso a la clave pública se debe especificar en el './.config/config.json' o poner en el directorio '.config' que es donde se busca por defecto.

Cada celda es encriptada con la clave privada y después hasheada mediante el algoritmo PBKDF2HMAC a una longitud fija de 10 caracteres. A continuación se guardan el texto encriptado y el hash (única para cada celda) en un diccionario clave-valor (siendo la clave el hash) en el archivo '.protected_data' y se introduce el hash del texto encriptado en la celda del excel. Esto se realiza para evitar saturar el excel con celdas de texto de gran longitud, como son los datos encriptados por RSA, y así, mantener la legibilidad.

Aquellos valores que se encuentren en la columna cuyo header se haya especificado que sea el 'id_field', serán hasheados con el mismo algoritmo de antes y encriptados de forma simétrica con la clave de acceso al programa, de tal forma que sea posible saber sin conocer la clave privada (sí se necesita la clave de acceso al programa), si dado un posible valor para un identificador, este se encuentra en el excel. Esto solo se realizará si el identificador seleccionado se encuentra en la lista de datos sensibles a encriptar. Por ejemplo, sirve para que un usuario que esté añadiendo nuevos pacientes, sepa si el paciente que va a añadir, ya ha sido añadido al excel o no antes, utilizando su número de historia como identificador. Estos sabrán a que fila del excel corresponde ese paciente y por tanto tendrán acceso a la información no encriptada (número de paciente que es, su género, la agudeza visual...) y por tanto relacionar en el dataset quien es el paciente y saber en que carpeta debe exportar sus imágenes.

En cuanto a la contraseña de acceso al programa, esta es almacenada en el archivo './.data/.login'. En este archivo se almacena el hash, derivado con la sal por defecto que se encuentra en el archivo 'login.py' (esta sal solo se usa para hashear esta contraseña y nada más), junto con otra sal generada de forma aleatoria, la cual sirve para crear de forma conjunta con la contraseña que se introduce por el programa, la contraseña real de 32 bytes que se utiliza en el programa (se aumenta la fuerza y longitud de la contraseña original, aunque sigue siendo vital utilizar una contraseña base fuerte).