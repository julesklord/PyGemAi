# Gemini CLI Chatbot: Tu Asistente de IA Avanzado en la Terminal

Este proyecto ofrece un chatbot de línea de comandos (CLI) interactivo y robusto que se conecta a la potente API de Google Gemini. Ha sido diseñado para proporcionar respuestas conversacionales inteligentes y fluidas, incorporando características esenciales como la gestión segura de claves API, una selección de modelos de IA personalizable y la persistencia del historial de chat para una experiencia de usuario continua y eficiente.

## ✨ Características Principales Detalladas

Este chatbot no es solo una simple interfaz; está repleto de funcionalidades pensadas para el usuario:

* **Chat Interactivo y Dinámico:** Experimenta conversaciones naturales y fluidas con una variedad de modelos de Google Gemini directamente desde la comodidad de tu terminal. La interfaz está diseñada para ser intuitiva, permitiéndote concentrarte en la interacción con la IA.

* **Gestión Segura y Flexible de API Key:** La seguridad de tu clave API es primordial.
    * **Carga desde Variable de Entorno:** Para una máxima seguridad y facilidad de configuración en entornos de desarrollo y producción, el chatbot puede cargar tu `GOOGLE_API_KEY` directamente desde las variables de entorno de tu sistema.
    * **Almacenamiento Local Opcional:** Si lo prefieres, puedes guardar tu clave API localmente.
        * **Encriptada (Recomendado):** Utiliza un sistema de encriptación fuerte (PBKDF2HMAC para derivación de clave y Fernet para la encriptación simétrica) protegido por una contraseña que tú elijas. Esto asegura que tu clave esté protegida incluso si alguien accede al archivo.
        * **Sin Encriptar (No Recomendado):** Para pruebas rápidas o entornos muy controlados, puedes optar por guardarla en texto plano, aunque esto conlleva riesgos de seguridad.
    * **Manejo Inteligente de Contraseña:** Se proporcionan múltiples intentos para ingresar la contraseña de desencriptación, y se ofrecen opciones para manejar archivos corruptos o contraseñas olvidadas, minimizando la frustración del usuario.

* **Selección de Modelo Inteligente y Personalizada:** Accede al modelo de IA que mejor se adapte a tus necesidades.
    * **Listado Completo:** El script consulta y lista todos los modelos de Gemini disponibles para generación de contenido a los que tienes acceso con tu clave API.
    * **Ordenación Estratégica:** Los modelos se presentan en un orden lógico, priorizando generalmente las versiones más recientes o capaces (como "latest", "pro", "flash") para que puedas acceder rápidamente a la tecnología más avanzada.
    * **Memoria de Modelo:** El chatbot recuerda el último modelo que utilizaste en una sesión anterior (guardado en `.gemini_chatbot_prefs.json`) y lo preselecciona automáticamente si sigue disponible, agilizando el inicio de nuevas conversaciones.

* **Persistencia del Historial de Chat Significativa:** No pierdas el hilo de tus conversaciones importantes.
    * **Carga Opcional:** Al iniciar una nueva sesión con un modelo, tienes la opción de cargar el historial de conversaciones previas mantenidas con ese mismo modelo.
    * **Guardado Selectivo:** Al finalizar tu sesión, puedes elegir guardar la conversación actual. Esto es ideal para retomar ideas, revisar información o simplemente mantener un registro de tus interacciones.
    * **Organización por Modelo:** Los archivos de historial se nombran de forma única según el modelo utilizado (ej. `chat_history_gemini-1.5-pro-latest.json`), manteniendo tus diferentes líneas de conversación organizadas y separadas.

* **Interfaz de Usuario Mejorada para Mayor Claridad:** La interacción debe ser agradable y eficiente.
    * **Uso de Colores ANSI:** Se emplean códigos de color en la terminal para distinguir claramente los mensajes del usuario, las respuestas del chatbot, las advertencias y las notificaciones del sistema, mejorando significativamente la legibilidad.
    * **Respuestas en *Streaming*:** Las respuestas del modelo se muestran palabra por palabra (o token por token) a medida que se generan, proporcionando una sensación de interacción en tiempo real y permitiéndote leer mientras la IA "piensa", en lugar de esperar una respuesta completa en bloque.

* **Preferencias de Usuario para una Experiencia Coherente:** El chatbot aprende tus hábitos.
    * **Almacenamiento del Último Modelo:** Como se mencionó, el último modelo seleccionado se guarda en un archivo de preferencias (`.gemini_chatbot_prefs.json`). Esto significa que no tienes que buscar tu modelo favorito cada vez que inicias el script, haciendo que el proceso sea más rápido y personalizado.

## 📋 Prerrequisitos Esenciales

Antes de sumergirte, asegúrate de tener lo siguiente:

* **Python:** Versión 3.8 o superior. Es crucial tener una versión moderna de Python para asegurar la compatibilidad con todas las bibliotecas y características del lenguaje utilizadas. Puedes verificar tu versión con `python --version` o `python3 --version`.
* **`pip` (Python Package Installer):** El manejador de paquetes estándar de Python, usualmente incluido con las instalaciones de Python. Necesario para instalar las bibliotecas de las que depende el chatbot. Puedes verificar si está instalado y actualizado.
* **Una Clave API de Google Gemini:** Esta es tu llave de acceso a los modelos de IA de Google. Puedes obtenerla registrándote y creándola en [Google AI Studio](https://aistudio.google.com/). ¡Trátala con la misma seguridad que una contraseña!

## 🚀 Guía Detallada de Instalación

Sigue estos pasos para poner en marcha el chatbot:

1.  **Obtén el Código Fuente:**
    * **Opción A: Clonar el Repositorio (si está disponible en Git):**
        ```bash
        git clone <URL_DEL_REPOSITORIO_SI_EXISTE>
        cd <NOMBRE_DEL_DIRECTORIO_DEL_REPOSITORIO>
        ```
    * **Opción B: Descargar el Script Individualmente:**
        Si solo tienes el archivo de script (ej. `gemini_chatbot.py`), descárgalo y guárdalo en un directorio de tu elección en tu sistema.

2.  **Configura un Entorno Virtual (Altamente Recomendado):**
    Los entornos virtuales aíslan las dependencias de tu proyecto, evitando conflictos con otros proyectos de Python en tu sistema.
    ```bash
    python -m venv .venv 
    ```
    Una vez creado, actívalo:
    * En Windows (cmd):
        ```bash
        .venv\Scripts\activate
        ```
    * En Windows (PowerShell):
        ```bash
        .venv\Scripts\Activate.ps1
        ```
    * En macOS y Linux:
        ```bash
        source .venv/bin/activate
        ```
    Verás el nombre del entorno (ej. `(.venv)`) al principio de tu prompt de terminal, indicando que está activo.

3.  **Instala las Dependencias Necesarias:**
    El chatbot depende de dos bibliotecas principales: `google-generativeai` para interactuar con la API de Gemini y `cryptography` para la encriptación segura de la clave API.
    * **Opción A: Usando `requirements.txt`:**
        Crea un archivo llamado `requirements.txt` en el directorio de tu proyecto con el siguiente contenido:
        ```txt
        google-generativeai
        cryptography
        ```
        Luego, instala todas las dependencias listadas ejecutando:
        ```bash
        pip install -r requirements.txt
        ```
    * **Opción B: Instalación Directa:**
        Puedes instalar cada biblioteca individualmente:
        ```bash
        pip install google-generativeai cryptography
        ```

4.  **Configura tu Clave API de Google Gemini:**
    El script necesita acceso a tu clave API para funcionar.
    * **Opción A (Más Segura y Recomendada para Desarrollo): Variable de Entorno:**
        Establece una variable de entorno llamada `GOOGLE_API_KEY` con el valor de tu clave.
        * En Linux/macOS (temporalmente para la sesión actual de la terminal):
            ```bash
            export GOOGLE_API_KEY="TU_API_KEY_VA_AQUI"
            ```
            Para hacerlo permanente, añádelo a tu archivo de configuración de shell (ej. `~/.bashrc`, `~/.zshrc`) y luego ejecuta `source ~/.bashrc` (o el archivo correspondiente) o reinicia la terminal.
        * En Windows (temporalmente para la sesión actual de cmd):
            ```bash
            set GOOGLE_API_KEY="TU_API_KEY_VA_AQUI"
            ```
        * En Windows (temporalmente para la sesión actual de PowerShell):
            ```bash
            $env:GOOGLE_API_KEY="TU_API_KEY_VA_AQUI"
            ```
            Para hacerlo permanente en Windows, busca "variables de entorno" en la configuración del sistema.
    * **Opción B: Interacción con el Script:**
        Si el script no detecta la variable de entorno `GOOGLE_API_KEY` ni un archivo de clave guardado previamente, te solicitará que ingreses la clave directamente en la terminal durante su ejecución. Luego tendrás la opción de guardarla (encriptada o no) para futuras sesiones.

## ▶️ Inicio Rápido y Uso

Con todos los prerrequisitos y la instalación completados, ejecutar el chatbot es sencillo:

1.  **Abre tu terminal o línea de comandos.**
2.  **Navega al directorio** donde guardaste el script `gemini_chatbot.py` y donde activaste tu entorno virtual (si usaste uno).
3.  **Ejecuta el script** usando Python:
    ```bash
    python gemini_chatbot.py
    ```

Al ejecutarlo por primera vez (o si no hay una clave API configurada), el script te guiará a través del proceso de configuración de la clave API. Posteriormente, te presentará la lista de modelos de IA disponibles para que selecciones con cuál deseas interactuar. Simplemente sigue las instrucciones que aparecen en pantalla. Una vez seleccionado el modelo, ¡estarás listo para chatear!

## 📄 Licencia

Este proyecto se distribuye bajo los términos de la Licencia GNUGPL V3. Por favor, consulta el archivo `LICENSE` (o `LICENSE.txt`) que se incluye con este proyecto para obtener el texto completo y los detalles específicos de los permisos y condiciones.
