# Changelog - (PyGemAi) - Gemini API Call Script
### This document details the modifications made to the Python script for interacting with the Gemini API.

## Initial Version (V1.0)
*   Basic implementation to configure the API with a key (from environment variable or code).
*   Examples of API calls:
    *   Simple text generation (single turn) using `model.generate_content()`.
    *   Starting and managing a conversation (multiple turns) using `model.start_chat()` and `chat.send_message()`.
*   Use of a fixed model name (`'gemini-pro'`).

## Addition of Model Selection by Name (V1.01)
*   Added the function to list all available models via `genai.list_models()`.
*   Filtered models to include only those that support content generation (`'generateContent'`).
*   Implemented a prompt for the user to enter the exact name of the model they wished to use.

## API Key Prompt if Not in Environment (V1.02)
*   Modified API key loading logic to first check the `GOOGLE_API_KEY` environment variable.
*   If the environment variable is not set, the user is prompted to enter the API key directly in the console.
*   Added basic error handling if no key is entered.

## Model Selection by Number and Default Option (V1.03)
*   Modified the presentation of available models to list them with a sequential number.
*   Implemented sorting logic to try to place the most recent or "latest" versions of models at the top of the list.
*   The first model in the sorted list was set as the default option.
*   Allowed the user to select a model by entering its corresponding number.
*   Added the option to press Enter (empty input) to automatically select the default model.
*   Included validation to ensure the entered number is valid and within range.

## Visual Improvements and `AttributeError` Fix (V1.04)
*   Introduced ANSI codes to add colors and styles (bold, underline) to the terminal output, improving visual presentation.
*   Added short pauses (`time.sleep`) to simulate processing times and make execution more readable.
*   **Bug Fix:** Removed an incorrect check that caused an `AttributeError` when trying to access `supported_generation_methods` on the `GenerativeModel` object instead of the listed model's information.

## Removal of API Call Examples (V1.05)
*   Removed code sections that made example API calls (`generate_content` and the multi-turn chat).
*   The script now exits after successful model selection, thus avoiding API quota consumption for these examples.

## Visualization of Models Not Available for Generation (V1.06)
*   Modified the model listing section to show *all* models obtained from the API.
*   Clearly separated models suitable for content generation (listed with numbers for selection) from those that are not.
*   Models not suitable for generation are listed separately, without numbering, and with a clear indication that they are not suitable for that task.

## "Chat" Start Message (V1.07)
*   Added a final message after successful model selection to inform the user which model they have "started a chat" with (in the context that this model is now selected for future interactions), although the script no longer initiates an actual chat session.

## Encrypted Local API Key Storage (V1.1)
*   Added functionality to save the API key in a local file, encrypted with a user-provided password.
*   Uses `cryptography` library for PBKDF2-based key derivation and Fernet for symmetric encryption.
*   Prompts for a password to encrypt and decrypt the key.
*   Prioritizes loading the API key from this encrypted file if it exists.
*   Offers to save the key in this encrypted format if entered manually or loaded from an environment variable.
*   Includes error handling for incorrect passwords and corrupted files, with an option to delete the problematic file.

## Unencrypted Local API Key Storage (V1.1.2)
*   Added an option to save the API key in a local file in plain text (unencrypted).
*   **Strong warnings** are displayed to the user about the security risks of this method.
*   The script will attempt to load from an unencrypted file if an encrypted one is not found or fails to load.
*   When a new key is provided, the user is given a choice to save it encrypted, unencrypted, or not at all.
*   Includes basic file handling and an option to delete a problematic unencrypted key file.

This log summarizes the evolution of the script through its different iterations.

### SPANISH - ESPAÑOL

# Registro de Cambios - Script de Llamada a la API de Gemini

### Este documento detalla las modificaciones realizadas en el script Python para interactuar con la API de Gemini.

## Versión Inicial
* Implementación básica para configurar la API con una clave (desde variable de entorno o código).
* Ejemplos de llamadas a la API:
    * Generación de texto simple (un solo turno) usando `model.generate_content()`.
    * Inicio y manejo de una conversación (múltiples turnos) usando `model.start_chat()` y `chat.send_message()`.
* Uso de un nombre de modelo fijo (`'gemini-pro'`).

## Adición de Selección de Modelo por Nombre
* Se añadió la función para listar todos los modelos disponibles a través de `genai.list_models()`.
* Se filtraron los modelos para incluir solo aquellos que soportan la generación de contenido (`'generateContent'`).
* Se implementó una solicitud al usuario para que ingresara el nombre exacto del modelo que deseaba utilizar.

## Solicitud de Clave API si no está en Entorno
* Se modificó la lógica de carga de la clave API para verificar primero la variable de entorno `GOOGLE_API_KEY`.
* Si la variable de entorno no está configurada, se solicita al usuario que ingrese la clave API directamente en la consola.
* Se añadió manejo básico de errores si no se ingresa ninguna clave.

## Selección de Modelo por Número y Opción por Defecto
* Se modificó la presentación de los modelos disponibles para listarlos con un número secuencial.
* Se implementó una lógica de ordenamiento para intentar colocar la versión más reciente o "latest" de los modelos al principio de la lista.
* El primer modelo de la lista ordenada se estableció como la opción por defecto.
* Se permitió al usuario seleccionar un modelo ingresando su número correspondiente.
* Se añadió la opción de presionar Enter (input vacío) para seleccionar automáticamente el modelo por defecto.
* Se incluyó validación para asegurar que el número ingresado sea válido y esté dentro del rango.

## Mejoras Visuales y Corrección de Error (`AttributeError`)
* Se introdujeron códigos ANSI para añadir colores y estilos (negrita, subrayado) a la salida de la terminal, mejorando la presentación visual.
* Se añadieron pausas cortas (`time.sleep`) para simular tiempos de procesamiento y hacer la ejecución más legible.
* **Corrección de Bug:** Se eliminó una verificación incorrecta que causaba un `AttributeError` al intentar acceder a `supported_generation_methods` en el objeto `GenerativeModel` en lugar de la información del modelo listado.

## Eliminación de Ejemplos de Llamada a la API
* Se eliminaron las secciones de código que realizaban llamadas de ejemplo a la API (`generate_content` y el chat de múltiples turnos).
* El script ahora finaliza después de la selección exitosa del modelo, evitando así el consumo de cuota de la API para estos ejemplos.

## Visualización de Modelos No Disponibles para Generación
* Se modificó la sección de listado de modelos para mostrar *todos* los modelos obtenidos de la API.
* Se separaron claramente los modelos aptos para generación de contenido (listados con números para selección) de aquellos que no lo son.
* Los modelos no aptos para generación se listan por separado, sin numerar, y con una indicación clara de que no son adecuados para esa tarea.

## Mensaje de Inicio de "Chat"
* Se añadió un mensaje final después de la selección exitosa del modelo para informar al usuario con qué modelo ha "iniciado un chat" (en el contexto de que ese modelo está ahora seleccionado para futuras interacciones), aunque el script ya no inicia una sesión de chat real.

## Almacenamiento Local Encriptado de Clave API
*   Se añadió la funcionalidad para guardar la clave API en un archivo local, encriptada con una contraseña proporcionada por el usuario.
*   Utiliza la biblioteca `cryptography` para derivación de clave basada en PBKDF2 y Fernet para encriptación simétrica.
*   Solicita una contraseña para encriptar y desencriptar la clave.
*   Prioriza la carga de la clave API desde este archivo encriptado si existe.
*   Ofrece guardar la clave en este formato encriptado si se ingresa manualmente o se carga desde una variable de entorno.
*   Incluye manejo de errores para contraseñas incorrectas y archivos corruptos, con opción de eliminar el archivo problemático.

## Almacenamiento Local Sin Encriptar de Clave API
*   Se añadió una opción para guardar la clave API en un archivo local en texto plano (sin encriptar).
*   Se muestran **fuertes advertencias** al usuario sobre los riesgos de seguridad de este método.
*   El script intentará cargar desde un archivo sin encriptar si no se encuentra uno encriptado o si falla la carga del mismo.
*   Cuando se proporciona una nueva clave, se le da al usuario la opción de guardarla encriptada, sin encriptar o no guardarla.
*   Incluye manejo básico de archivos y una opción para eliminar un archivo de clave sin encriptar problemático.

Este registro resume la evolución del script a través de las diferentes iteraciones.