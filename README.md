# PyGemAi: Chatbot CLI para Modelos Google Gemini

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)

PyGemAi es una aplicación de línea de comandos (CLI) que te permite interactuar de forma sencilla y eficiente con los modelos de Inteligencia Artificial de Google Gemini directamente desde tu terminal.

## Características Principales

* **Interfaz de Chat Intuitiva:** Conversa con los modelos Gemini de forma fluida.
* **Gestión Segura de Clave API:**
  * Soporte para carga desde variable de entorno (`GOOGLE_API_KEY`).
  * Opción para guardar la clave API localmente de forma encriptada con contraseña.
  * Opción para guardar sin encriptar (no recomendado) o no guardar localmente.
  * Manejo de intentos de contraseña y eliminación segura de archivos de clave corruptos.
* **Selección Dinámica de Modelos:**
  * Lista y permite seleccionar entre los modelos Gemini disponibles para generación de contenido.
  * Ordena los modelos por relevancia (priorizando "latest", "pro", "flash").
  * Recuerda y sugiere el último modelo utilizado.
* **Historial de Conversaciones:**
  * Opción para cargar el historial de chat previo para un modelo específico.
  * Opción para guardar la sesión de chat actual al finalizar.
  * Los historiales se guardan en archivos `.json` separados por modelo.
* **Personalización:**
  * Guarda las preferencias del último modelo usado.
  * Uso de colores ANSI para una mejor legibilidad en la terminal.
* **Empaquetado y Listo para Usar:** Configurado con `setup.py` y `pyproject.toml` para una fácil instalación y uso del comando `pygemai`.

## Requisitos Previos

* Python 3.8 o superior.
* `pip` (el gestor de paquetes de Python).
* Una Clave API de Google Gemini válida (puedes obtenerla en [Google AI Studio](https://aistudio.google.com/)).

## Instalación

1. **Clona el Repositorio:**
    (Reemplaza `TU_USUARIO_GITHUB/PyGemAi.git` con la URL real de tu repositorio)

    ```bash
    git clone [https://github.com/TU_USUARIO_GITHUB/PyGemAi.git](https://github.com/TU_USUARIO_GITHUB/PyGemAi.git)
    cd PyGemAi
    ```

2. **Crea y Activa un Entorno Virtual (Recomendado):**

    ```bash
    python3 -m venv .venv
    ```

    Activación (ejemplos):
    * Linux/macOS (bash/zsh): `source .venv/bin/activate`
    * Linux/macOS (fish): `source .venv/bin/activate.fish`
    * Windows (cmd): `.venv\Scripts\activate.bat`
    * Windows (PowerShell): `.venv\Scripts\Activate.ps1`

3. **Instala PyGemAi y sus Dependencias:**
    Desde el directorio raíz del proyecto (donde está `setup.py`), ejecuta:

    ```bash
    pip install -e .
    ```

    Esto instalará el paquete `PyGemAi` en modo editable y el comando `pygemai` estará disponible mientras tu entorno virtual esté activado. Las dependencias principales son `google-generativeai` y `cryptography`.

## Configuración de la Clave API

Al ejecutar `pygemai` por primera vez, o si no se detecta una clave API, se te guiará para configurarla. Tienes varias opciones:

* Usar la variable de entorno `GOOGLE_API_KEY`.
* Ingresarla manualmente y elegir guardarla de forma encriptada (recomendado), sin encriptar, o no guardarla.

Para más detalles sobre la configuración y gestión de la clave API, consulta la [Guía de Uso detallada (`GUIDE_OF_USE.md`)](GUIDE_OF_USE.md).

## Uso Básico

Una vez instalado y configurada la clave API:

1. **Ejecuta el Chatbot:**
    Abre tu terminal (con el entorno virtual activado) y escribe:

    ```bash
    pygemai
    ```

2. **Selecciona un Modelo:** Sigue las instrucciones en pantalla para elegir un modelo de IA.
3. **Chatea:** Escribe tus mensajes y presiona Enter.
4. **Sal del Chat:** Escribe `salir`, `exit`, `quit`, o presiona `Ctrl+C`.
5. **Guarda el Historial:** Se te preguntará si deseas guardar el historial de la sesión.

Para una explicación completa de todas las características, opciones de línea de comandos (si las hubiera en el futuro), y solución de problemas, por favor consulta la [**Guía de Uso (`GUIDE_OF_USE.md`)**](GUIDE_OF_USE.md).

## Estructura del Proyecto (para Desarrolladores)

Este proyecto utiliza una estructura `src/` donde el paquete principal `pygemai_cli` contiene la lógica de la aplicación (`main.py`).

## Contribuciones

Las contribuciones son bienvenidas. Por favor, abre un *issue* para discutir cambios importantes o reportar errores. Si deseas contribuir con código, considera hacer un *fork* del repositorio y enviar un *pull request*.

## Licencia

Este proyecto está licenciado bajo los términos de la **GNU General Public License v3.0 o posterior**.
Consulta el archivo [LICENSE](LICENSE) para más detalles.

Copyright (C)  <Julio César Martínez> <julioglez@gmail.com>

Este programa es software libre: usted puede redistribuirlo y/o modificarlo
bajo los términos de la Licencia Pública General GNU publicada por la Fundación
para el Software Libre, ya sea la versión 3 de la Licencia, o (a su opción)
cualquier versión posterior.

Este programa se distribuye con la esperanza de que sea útil, pero SIN NINGUNA
GARANTÍA; sin siquiera la garantía implícita de COMERCIABILIDAD o IDONEIDAD
PARA UN PROPÓSITO PARTICULAR. Consulte la Licencia Pública General GNU para más detalles.  

Usted debería haber recibido una copia de la Licencia Pública General GNU junto
con este programa. Si no, consulte <https://www.gnu.org/licenses/>.  

## Contacto

Julio César Martínez - <julioglez@gmail.com>

---

Desarrollado con ❤️ y Python.
