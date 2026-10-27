# PPS-E1 · Lectura entrada→sink

Cópiala como `PPS-E1-lectura.md` y rellénala.

| `Validar.java` (bytecode / JVM):
	- Punto de entrada: Los argumentos de la línea de comandos recogidos a través de args[0] en el método main, que se pasan al parámetro nombre en la función buscarUsuario.
	- Validación: Se utiliza la función validarNombre(nombre), la cual comprueba que el nombre no sea nulo, que su longitud sea mayor que 0 y menor o igual a 32 caracteres.
		- ¿Sirve para algo?: Sirve únicamente para controlar restricciones de longitud y evitar nulos, pero no previene ataques, ya que permite cualquier carácter (incluyendo comillas simples ') siempre y cuando la longitud esté dentro del rango permitido.

	- Sink: La línea st.executeQuery(consulta) donde se concatena directamente la variable nombre en la sentencia SQL (SELECT * FROM usuarios WHERE nombre = '...'). Esto genera una vulnerabilidad crítica de Inyección SQL.
	- Por qué falla: Java compila el código a bytecode para ejecutarse sobre la Máquina Virtual de Java (JVM). La pista del código nos señala que el bytecode es fácilmente descompilable utilizando herramientas como jadx o procyon. Esto significa que cualquier atacante puede recuperar la lógica interna y descubrir elementos sensibles incrustados en el código (como la clave de API hardcodeada apiKey = "LAB-DEMO-NO-REAL-1234"). No obstante, el fallo principal de seguridad radica en la concatenación de cadenas para formar consultas SQL en lugar de utilizar consultas parametrizadas (Prepared Statements).

| `validar.py`(interpretado):
	- Punto de entrada: Los argumentos de la línea de comandos recogidos a través de sys.argv[1], que se pasan al parámetro nombre de la función buscar_usuario.
	- Validación: Se utiliza la función validar_nombre(nombre), que comprueba que la longitud sea mayor que 0 y menor o igual a 32 caracteres.
		- ¿Sirve para algo?: Sirve para asegurar que el dato no esté vacío y cumpla con el límite de longitud, pero no sirve para la seguridad, ya que permite cualquier tipo de carácter especial que altere la lógica del programa.
	
	- Sink: Dispone de varios sinks críticos: por un lado las consultas que generan inyección SQL (con.execute), y por otro y principal, eval(regla), donde se evalúa y ejecuta una cadena de texto como si fuera código de Python.
	- Por qué falla: Python es un lenguaje interpretado donde el código fuente o las cadenas de texto pueden ser evaluadas dinámicamente en tiempo de ejecución. Al usar la función eval() con datos manipulados por el usuario sin desinfectar, cualquier atacante puede inyectar código arbitrario de Python para que el intérprete lo ejecute con los permisos de la aplicación.


| `validar.c` (nativo):
	- Punto de entrada: Los argumentos de la línea de comandos recogidos a través de argv[1] en la función main, que se pasan al parámetro nombre de la función buscar_usuario.
	- Validación: No existe ninguna validación ni control de tamaño en el código de C. El programa confía plenamente en lo que recibe.
		- ¿Sirve para algo?: Al no existir validación, no sirve para nada a nivel de seguridad ni de control de datos.

	- Sink: La función clásica de copia de cadenas strcpy(buffer, nombre), donde se copian los datos de entrada a un búfer estático de tamaño fijo (char buffer[32];).
	- Por qué falla: C es un lenguaje compilado directamente a código nativo que carece de seguridad de memoria y de límites automáticos. Al usar strcpy sin comprobar la longitud, si el dato de entrada supera los 31 caracteres, se produce un desbordamiento de búfer (Buffer Overflow) que sobrescribe la memoria contigua de la pila (stack), pudiendo corromper la ejecución o comprometer el sistema.
	

## ¿Cómo lo corregirías? (una línea por fichero)

- `validar.py`: Sustituir el uso peligroso de eval() por una lógica segura y validar estrictamente los datos de entrada.
- `Validar.java`: Utilizar consultas parametrizadas (Prepared Statements) en lugar de concatenar cadenas directamente en la sentencia SQL.
- `validar.c`: Reemplazar la función insegura strcpy por una alternativa segura que controle límites (como strncpy o snprintf).


- Preguntas:

1. ¿Cuál es el sink más peligroso de validar.py? ¿Por qué?

El sink más peligroso es eval() (linea 30), aunque tambien existe una inyección SQL en la consulta (linea 25) y un command injection en os.system() (linea 27).

Porque eval() interpreta y ejecuta cadenas de texto como código de Python. Al concatenar directamente la entrada del usuario (nombre) sin sanear, permite la inyección y ejecución de código arbitrario en el sistema, provocando un fallo crítico de seguridad propio de los leguajes interpretados.


2. ¿Qué cobertura tenía descuentos.py con el fallo dentro?

Cobertura del 83% (con la línea 24 sin cubrir).


3. ¿Qué mensaje te dió pytest cuando tu test fallaba?

Dio el mensaje: Failed: DID NOT RAISE ValueError en la línea 25 de test_descuentos.py.

Significa que el test falló correctamente porque esperaba que la función lanzara una excepción ValueError ante valores incorrectos (como 150% o -5%). pero la función no la lanzó y se ejecutó sin rechazar dichos valores.


4. ¿Qué valores encontró fuzzing que tus test no habían probado?

Valores extremos y anómalos: Encontró precios y porcentajes con números negativos (ej. precios y porcentajes de descuento negativos), valores infinitos (inf), y valores no numéricos (nan), además de porcentajes masivos (ej. 294.39, 999.31, 1e+308).
Estos casos extremos provocan resultados matemáticos absurdos o no válidos (como precios resultantes negativos, -inf o nan) que los test unitarios manuales (enfocados solo en descuentos normales de 0% a 100%) jamás se detienen a probar. El fuzzing los expuso al generar 20.000 combinaciones aleatorias de "estrés".
