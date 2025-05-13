# Gemini CLI Chatbot - Guía de Utilización

La presente guía tiene como objetivo proporcionar instrucciones detalladas para la instalación, configuración y operación del Chatbot Gemini mediante Interfaz de Línea de Comandos (CLI).

## Índice de Contenidos
1.  [Introducción](#1-introducción)
2.  [Proceso de Instalación y Configuración Sistemática](#2-proceso-de-instalación-y-configuración-sistemática)
    * [Requisitos Previos del Sistema](#requisitos-previos-del-sistema)
    * [Adquisición del Script y Gestión de Dependencias](#adquisición-del-script-y-gestión-de-dependencias)
    * [Configuración de la Clave de API](#configuración-de-la-clave-de-api)
3.  [Ejecución Inicial y Procedimientos de Primer Uso](#3-ejecución-inicial-y-procedimientos-de-primer-uso)
4.  [Selección Estratégica del Modelo de IA](#4-selección-estratégica-del-modelo-de-ia)
5.  [Interacción Conversacional y Gestión del Historial](#5-interacción-conversacional-y-gestión-del-historial)
6.  [Gestión de Preferencias y Consideraciones de Seguridad](#6-gestión-de-preferencias-y-consideraciones-de-seguridad)
7.  [Diagnóstico y Solución de Problemas Comunes](#7-diagnóstico-y-solución-de-problemas-comunes)

---
## 1. Introducción

El Chatbot Gemini CLI facilita la interacción con los modelos de Inteligencia Artificial de Google Gemini a través de una terminal de línea de comandos. Este sistema ofrece una gestión segura de claves de API, selección avanzada de modelos y la capacidad de preservar el historial de las conversaciones para una continuidad operativa.

## 2. Proceso de Instalación y Configuración Sistemática
### Requisitos Previos del Sistema
* **Python:** Versión 3.8 o superior.
* **pip:** El sistema de gestión de paquetes para Python.
* **Clave de API de Google Gemini:** Es indispensable obtener una clave de API válida a través de [Google AI Studio](https://aistudio.google.com/).

### Adquisición del Script y Gestión de Dependencias
1.  **Obtención del Script:** Descargue o clone el archivo `gemini_chatbot.py` en un directorio designado.
2.  **Entorno Virtual (Práctica Recomendada):**
    ```bash
    python -m venv .venv
    # Activación en Windows: .venv\Scripts\activate | Activación en macOS/Linux: source .venv/bin/activate
    ```
3.  **Instalación de Dependencias:** Se requieren las bibliotecas `google-generativeai` y `cryptography`. Genere un archivo `requirements.txt`:
    ```txt
    google-generativeai
    cryptography
    ```
    Proceda con la instalación mediante:
    ```bash
    pip install -r requirements.txt
    ```
    Alternativamente, instale directamente: `pip install google-generativeai cryptography`.

### Configuración de la Clave de API

La clave de API puede ser proporcionada al sistema mediante los siguientes métodos:
## 1.  **Variable de Entorno (Método Preferente):** Defina la variable de entorno `GOOGLE_API_KEY`.
    * **Linux/macOS (sesión temporal):** `export GOOGLE_API_KEY="SU_CLAVE_API"`
    * **Windows (cmd, sesión temporal):** `set GOOGLE_API_KEY="SU_CLAVE_API"`
    * **Windows (PowerShell, sesión temporal):** `$env:GOOGLE_API_KEY="SU_CLAVE_API"`
    Para una configuración persistente, consúltense los manuales correspondientes del sistema operativo.
## 2.  **Entrada Manual y Almacenamiento Local:** En ausencia de la variable de entorno o un archivo de configuración local, el script solicitará la clave directamente y ofrecerá opciones para su almacenamiento.

## 3. Ejecución Inicial y Procedimientos de Primer Uso

Navegue al directorio de ubicación del script y proceda con su ejecución:
```bash
python gemini_chatbot.py
```

Durante la primera ejecución sin una configuración previa, el sistema intentará obtener la GOOGLE_API_KEY secuencialmente desde: variables de entorno, archivos locales (.gemini_api_key_encrypted, .gemini_api_key_unencrypted), y finalmente, mediante solicitud directa al usuario.

Al ingresar la clave manualmente (o si fue cargada desde una variable de entorno sin un archivo local preexistente), se presentarán las siguientes opciones de almacenamiento:

    Almacenamiento Encriptado (Recomendado): Se solicitará una contraseña (mínimo 8 caracteres). La clave será almacenada de forma segura en .gemini_api_key_encrypted. Dicha contraseña será requerida en sesiones subsecuentes (se permiten 3 intentos).
    
    Almacenamiento Sin Encriptar (No Recomendado): La clave se guardará en texto plano en .gemini_api_key_unencrypted, lo cual constituye un riesgo de seguridad.
    
    No Almacenar: La clave se utilizará exclusivamente durante la sesión activa.

En caso de fallo del archivo encriptado (contraseña incorrecta/corrupción del archivo) tras tres intentos, o si un archivo no encriptado resulta ilegible, el sistema ofrecerá la opción de eliminar dicho archivo.

## 4. Selección Estratégica del Modelo de IA

Una vez configurada la API, se presentará un listado de los modelos Gemini disponibles, ordenados por relevancia (priorizando "latest", "pro", "flash" y versiones recientes).

    Modelo Predeterminado: Será el primer modelo de la lista (identificado como [Por Defecto]) o el último utilizado si aún se encuentra disponible (identificado como [Último Usado / Por Defecto]), cargado desde .gemini_chatbot_prefs.json.
    
    Proceso de Selección: Ingrese el numeral correspondiente al modelo deseado o presione Enter para utilizar el modelo predeterminado. El modelo seleccionado se registrará como preferencia.

## 5. Interacción Conversacional y Gestión del Historial

    Interacción: Ingrese su consulta después de la indicación Tú: y presione Enter. La respuesta del modelo (ej. gemini-1.5-pro:) se mostrará mediante transmisión en flujo (streaming).
    
    Finalización de Sesión: Ingrese salir, exit, quit o utilice la combinación de teclas Ctrl+C.
    Gestión del Historial de Conversación:
    
        Carga de Historial: Al iniciar una sesión, se consultará si desea cargar el historial previo asociado al modelo seleccionado desde chat_history_<nombre_modelo>.json. Responda S o presione Enter para cargar, o n para iniciar una nueva conversación.
        
        Guardado de Historial: Al finalizar la sesión, se ofrecerá la opción de guardar la conversación actual en el archivo correspondiente (sobrescribiendo versiones anteriores).

## 6. Gestión de Preferencias y Consideraciones de Seguridad

    Archivo de Preferencias (.gemini_chatbot_prefs.json): Almacena el último modelo utilizado. Se genera automáticamente si no existe.
    
    Seguridad de la Clave de API:
    
        La clave de API debe ser tratada con la misma confidencialidad que una contraseña.
        Se recomienda optar por el almacenamiento encriptado para claves locales.
        El script intenta aplicar permisos restrictivos (0o600) a los archivos de claves en sistemas Unix.
        El uso de variables de entorno es una práctica de seguridad robusta, particularmente en entornos de servidor.

## #7. Diagnóstico y Solución de Problemas Comunes

    "cryptography no instalada": Verifique y reinstale las dependencias.
    
    Errores de Clave de API: Confirme la validez y estado activo de su clave en Google AI Studio y asegúrese de no haber excedido las cuotas asignadas.
    
    Errores de Carga/Guardado de Archivos: Verifique los permisos de lectura/escritura en el directorio de ejecución del script.
    
    Modelo No Disponible: La inaccesibilidad puede deberse a restricciones regionales o de cuota. Considere utilizar un modelo alternativo.
    
    Respuesta Bloqueada: Si el contenido es interceptado por filtros de seguridad, el sistema lo notificará. Se sugiere reformular la consulta.
