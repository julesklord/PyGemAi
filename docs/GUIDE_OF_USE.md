# Guía de Uso: PyGemAi Chatbot CLI

## 1. Introducción

Bienvenido a PyGemAi, un chatbot de línea de comandos (CLI) que te permite interactuar con los potentes modelos de Inteligencia Artificial de Google Gemini. PyGemAi ofrece una gestión segura de tu clave API, selección avanzada de modelos y la capacidad de guardar y cargar el historial de tus conversaciones.

## 2. Requisitos Previos

Antes de usar PyGemAi, asegúrate de tener lo siguiente:

* **Python:** Versión 3.8 o superior.
* **Pip:** El gestor de paquetes de Python (generalmente viene con Python).
* **Dependencias de Python:** (Se instalan automáticamente con el proyecto)
  * `google-generativeai`
  * `cryptography`
* **Clave API de Google Gemini:** Necesitarás una clave API válida. Puedes obtenerla desde [Google AI Studio](https://aistudio.google.com/).
* **Git:** (Opcional, si clonas el repositorio desde GitHub).

## 3. Instalación

Puedes instalar PyGemAi de la siguiente manera:

### 3.1. Desde el Código Fuente (usando Git)

1. **Clona el repositorio (si está en GitHub):**

    ```bash
    git clone https://github.com/spjulius/PyGemAi.git
    ```

    ```bash
    cd PyGemAi
    ```

2. **Crea y activa un entorno virtual (recomendado):**

    ```bash
    python3 -m venv .venv
    ```

   ## En Linux/macOS (bash/zsh)

    ```zsh
    source .venv/bin/activate
    ```

   ## En Linux/macOS (fish)

    ```fish
    source .venv/bin/activate.fish
    ```

   ## En Windows (cmd)

    ```cmd
    .venv\Scripts\activate.bat
    ```

   ## En Windows (PowerShell)

    ```powershell
    .venv\Scripts\Activate.ps1
    ```

3. **Instala el paquete en modo editable:**
    Esto instalará las dependencias necesarias y el comando `pygemai`.

    ```bash
    pip install -e .
    ```

## 4. Configuración Inicial (Primera Ejecución)

### 4.1. Obtención de la Clave API de Google Gemini

Antes de poder chatear, PyGemAi necesita tu clave API de Google Gemini. Si no tienes una, visita [Google AI Studio](https://aistudio.google.com/) para crear una.

### 4.2. Configuración de la Clave API en PyGemAi

Cuando ejecutes `pygemai` por primera vez (o si no encuentra una clave API guardada), intentará obtener la clave en el siguiente orden:

1. **Variable de Entorno (Método Preferente):**
    Puedes definir la variable de entorno `GOOGLE_API_KEY` con tu clave. PyGemAi la detectará automáticamente.
    * Linux/macOS (sesión temporal): `export GOOGLE_API_KEY="TU_CLAVE_API"`
    * Windows (cmd, sesión temporal): `set GOOGLE_API_KEY="TU_CLAVE_API"`
    * Windows (PowerShell, sesión temporal): `$env:GOOGLE_API_KEY="TU_CLAVE_API"`
    (Para configuración persistente, consulta la documentación de tu sistema operativo).

2. **Archivos Locales:** Buscará los archivos `.gemini_api_key_encrypted` o `.gemini_api_key_unencrypted`.

3. **Ingreso Manual y Almacenamiento:**
    Si no se encuentra ninguna clave, PyGemAi te pedirá que la ingreses directamente. Luego, te ofrecerá las siguientes opciones para guardarla para futuros usos:

    * **1. Encriptada (Recomendado):**
        * Se te pedirá una contraseña (mínimo 8 caracteres).
        * Tu clave API se guardará de forma segura en el archivo `.gemini_api_key_encrypted`.
        * Necesitarás ingresar esta contraseña cada vez que inicies PyGemAi (tienes 3 intentos).
    * **2. Sin Encriptar (No Recomendado):**
        * Tu clave API se guardará en texto plano en el archivo `.gemini_api_key_unencrypted`.
        * **Advertencia:** Esto es un riesgo de seguridad si alguien más accede a tu sistema.
    * **3. No Guardar (o presionar Enter):**
        * La clave API se usará solo para la sesión actual y no se guardará localmente. Deberás ingresarla cada vez.

### 4.3. Gestión de Contraseñas y Archivos de Clave

* **Contraseña Incorrecta (Clave Encriptada):** Si ingresas la contraseña incorrecta 3 veces para una clave encriptada, PyGemAi te preguntará si deseas eliminar el archivo `.gemini_api_key_encrypted` (ya que podría estar corrupto o la contraseña olvidada).
* **Archivo Ilegible (Clave Sin Encriptar):** Si el archivo `.gemini_api_key_unencrypted` existe pero no se puede leer o está vacío, también se te ofrecerá la opción de eliminarlo.

## 5. Ejecución del Chatbot

Una vez instalado y configurada la clave API (si es necesario), puedes iniciar el chatbot desde cualquier lugar en tu terminal (siempre que el entorno virtual esté activado, si lo usaste para la instalación):

```bash
pygemai
```

## 6. Interacción con el Chatbot

### 6.1. Selección del Modelo de IA

Al iniciar, PyGemAi listará los modelos de Gemini disponibles para generación de contenido, ordenados por relevancia (priorizando "latest", "pro", "flash"):

* Se te presentará una lista numerada de modelos.
  * **Modelo por Defecto:**
    * Si es la primera vez o el último modelo usado no está disponible, el primer modelo de la lista será el predeterminado.
    * Si usaste un modelo anteriormente y aún está disponible, ese será el predeterminado (indicado como `[Por defecto - Último usado]`).
  * **Para seleccionar:**
    * Ingresa el número correspondiente al modelo deseado y presiona Enter.
    * Simplemente presiona Enter para usar el modelo por defecto.
* El modelo que selecciones se guardará como preferencia para la próxima vez en el archivo `.gemini_chatbot_prefs.json`.

### 6.2. Carga del Historial de Chat

Después de seleccionar un modelo, PyGemAi te preguntará si deseas cargar el historial de chat anterior asociado con ese modelo específico.

* El archivo de historial se nombra `chat_history_<nombre_modelo_seguro>.json`.
* Presiona `<S>` o `<Enter>` para cargar el historial.
* Presiona `<n>` (y Enter) para iniciar una nueva conversación sin cargar el historial.

### 6.3. Chateando

Una vez en la sesión de chat:

* Verás un indicador `Tú:`. Escribe tu mensaje y presiona Enter.
* El modelo responderá. El nombre del modelo (ej. `gemini-1.5-pro-latest:`) precederá su respuesta. Las respuestas se muestran en tiempo real (streaming).

### 6.4. Finalizar la Sesión y Guardar Historial

Para terminar la conversación:

* Escribe `salir`, `exit`, o `quit` y presiona Enter.
* También puedes presionar `Ctrl+C`.

Al salir, PyGemAi te preguntará si deseas guardar el historial de la conversación actual en el archivo correspondiente (ej. `chat_history_<nombre_modelo_seguro>.json`).

* Presiona `<S>` o `<Enter>` para guardar (sobrescribirá el historial anterior para ese modelo).
* Presiona `<n>` (y Enter) para salir sin guardar el historial de la sesión actual.

## 7. Archivos Generados por PyGemAi

PyGemAi puede crear los siguientes archivos en el directorio desde donde lo ejecutes (o en el directorio raíz de tu proyecto si lo instalaste):

* `.gemini_api_key_encrypted`: Tu clave API guardada de forma encriptada (si elegiste esta opción).
* `.gemini_api_key_unencrypted`: Tu clave API guardada sin encriptar (si elegiste esta opción, no recomendado).
* `.gemini_chatbot_prefs.json`: Guarda el nombre del último modelo de IA que utilizaste.
* `chat_history_<nombre_modelo_seguro>.json`: Archivos que almacenan el historial de tus conversaciones para cada modelo.

## 8. Desinstalación (Opcional)

Si instalaste PyGemAi usando pip en un entorno virtual:

* Activa el entorno virtual.
* Ejecuta:

```bash
 pip uninstall PyGemAi
```

 Puedes eliminar la carpeta del entorno virtual y el directorio del proyecto si ya no los necesitas.

## 9. Solución de Problemas Comunes

```bash
 ModuleNotFoundError o ImportError para cryptography o google-generativeai:
 ```

 Asegúrate de haber instalado las dependencias. Si usas un entorno virtual, asegúrate de que esté activado y que las dependencias se instalaron dentro de él:

```bash
pip install google-generativeai cryptography
```

### Error al configurar la API / Error al listar modelos

 Verifica que tu clave API de Google Gemini sea correcta y esté activa.
 Asegúrate de tener conexión a internet.
 Si guardaste la clave encriptada, verifica que estás usando la contraseña correcta.

```bash
"Comando pygemai no encontrado":
```

 Asegúrate de haber instalado el paquete correctamente con pip install -e . (o pip install .).
 Si usas un entorno virtual, asegúrate de que esté activado en la terminal donde intentas ejecutar el comando.
 En algunos casos, podrías necesitar abrir una nueva terminal después de la instalación para que el sistema reconozca el nuevo comando.

### Prompt bloqueado por filtros de seguridad

 Si tu consulta es bloqueada, PyGemAi te lo notificará. Intenta reformular tu pregunta.
