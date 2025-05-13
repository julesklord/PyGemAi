import os
import re
import sys
import time
import getpass
import json  # Para guardar y cargar el historial y preferencias

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

# --- Dependencias para encriptación ---
try:
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import default_backend
    from cryptography.fernet import Fernet, InvalidToken
    import base64
except ImportError:
    print(
        "La biblioteca 'cryptography' no está instalada. Por favor, instálala con: pip install cryptography"
    )
    sys.exit(1)


# --- Definición de colores ANSI para la terminal ---
class Colors:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


# --- Constantes ---
ENCRYPTED_API_KEY_FILE = ".gemini_api_key_encrypted"
UNENCRYPTED_API_KEY_FILE = ".gemini_api_key_unencrypted"
PREFERENCES_FILE = ".gemini_chatbot_prefs.json"  # Para guardar el último modelo usado
SALT_SIZE = 16
ITERATIONS = 390_000


# --- Funciones de encriptación/desencriptación (sin cambios) ---
def _derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
        backend=default_backend(),
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def save_encrypted_api_key(api_key: str, password: str):
    try:
        salt = os.urandom(SALT_SIZE)
        derived_key = _derive_key(password, salt)
        f = Fernet(derived_key)
        encrypted_api_key = f.encrypt(api_key.encode())

        with open(ENCRYPTED_API_KEY_FILE, "wb") as key_file:
            key_file.write(salt)
            key_file.write(encrypted_api_key)
        print(
            f"{Colors.GREEN}API Key encriptada y guardada en {ENCRYPTED_API_KEY_FILE}{Colors.RESET}"
        )
        if os.name != "nt":
            os.chmod(ENCRYPTED_API_KEY_FILE, 0o600)
    except Exception as e:
        print(f"{Colors.RED}Error al guardar la API Key encriptada: {e}{Colors.RESET}")


def load_decrypted_api_key(password: str) -> str | None:
    if not os.path.exists(ENCRYPTED_API_KEY_FILE):
        return None
    try:
        with open(ENCRYPTED_API_KEY_FILE, "rb") as key_file:
            salt = key_file.read(SALT_SIZE)
            encrypted_api_key = key_file.read()

        derived_key = _derive_key(password, salt)
        f = Fernet(derived_key)
        decrypted_api_key = f.decrypt(encrypted_api_key).decode()
        return decrypted_api_key
    except InvalidToken:
        return None
    except Exception as e:
        print(f"{Colors.RED}Error al cargar la API Key encriptada: {e}{Colors.RESET}")
        return None


def save_unencrypted_api_key(api_key: str):
    try:
        with open(UNENCRYPTED_API_KEY_FILE, "w") as key_file:
            key_file.write(api_key)
        print(
            f"{Colors.YELLOW}{Colors.BOLD}ADVERTENCIA:{Colors.RESET}{Colors.YELLOW} API Key guardada SIN ENCRIPTAR en {UNENCRYPTED_API_KEY_FILE}.{Colors.RESET}"
        )
        # ... (resto de mensajes de advertencia)
        if os.name != "nt":
            os.chmod(UNENCRYPTED_API_KEY_FILE, 0o600)
    except Exception as e:
        print(
            f"{Colors.RED}Error al guardar la API Key sin encriptar: {e}{Colors.RESET}"
        )


def load_unencrypted_api_key() -> str | None:
    if not os.path.exists(UNENCRYPTED_API_KEY_FILE):
        return None
    try:
        with open(UNENCRYPTED_API_KEY_FILE, "r") as key_file:
            api_key = key_file.read().strip()
            if api_key:
                print(
                    f"{Colors.YELLOW}{Colors.BOLD}ADVERTENCIA:{Colors.RESET}{Colors.YELLOW} API Key cargada SIN ENCRIPTAR desde {UNENCRYPTED_API_KEY_FILE}.{Colors.RESET}"
                )
                return api_key
            # ... (resto de lógica)
            return None
    except Exception as e:
        print(
            f"{Colors.RED}Error al cargar la API Key desde el archivo sin encriptar: {e}{Colors.RESET}"
        )
        return None


# --- Funciones de Preferencias (Nuevo) ---
def save_preferences(prefs: dict):
    """Guarda las preferencias en un archivo JSON."""
    try:
        with open(PREFERENCES_FILE, "w", encoding="utf-8") as f:
            json.dump(prefs, f, ensure_ascii=False, indent=2)
        # print(f"{Colors.GREEN}Preferencias guardadas en {PREFERENCES_FILE}{Colors.RESET}") # Opcional: no mostrar este mensaje
    except Exception as e:
        print(f"{Colors.RED}Error al guardar las preferencias: {e}{Colors.RESET}")


def load_preferences() -> dict:
    """Carga las preferencias desde un archivo JSON."""
    if not os.path.exists(PREFERENCES_FILE):
        return {}  # Devuelve un diccionario vacío si no existe
    try:
        with open(PREFERENCES_FILE, "r", encoding="utf-8") as f:
            prefs = json.load(f)
        # print(f"{Colors.GREEN}Preferencias cargadas desde {PREFERENCES_FILE}{Colors.RESET}") # Opcional
        return prefs
    except Exception as e:
        print(
            f"{Colors.RED}Error al cargar las preferencias: {e}. Usando valores por defecto.{Colors.RESET}"
        )
        return {}


# --- Funciones de Historial de Chat (sin cambios en su lógica interna) ---
def get_chat_history_filename(model_name: str) -> str:
    safe_model_name = "".join(
        c if c.isalnum() or c in ("-", "_") else "_" for c in model_name
    )
    return f"chat_history_{safe_model_name}.json"


def save_chat_history(chat_session, filename: str):
    history_to_save = []
    for content in chat_session.history:
        parts_to_save = []
        for part in content.parts:
            if hasattr(part, "text"):
                parts_to_save.append({"text": part.text})
        history_to_save.append({"role": content.role, "parts": parts_to_save})
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(history_to_save, f, ensure_ascii=False, indent=2)
        print(f"{Colors.GREEN}Historial de chat guardado en {filename}{Colors.RESET}")
    except Exception as e:
        print(f"{Colors.RED}Error al guardar el historial: {e}{Colors.RESET}")


def load_chat_history(filename: str) -> list | None:
    if not os.path.exists(filename):
        return None
    try:
        with open(filename, "r", encoding="utf-8") as f:
            history = json.load(f)
        print(f"{Colors.GREEN}Historial de chat cargado desde {filename}{Colors.RESET}")
        return history
    except Exception as e:
        print(
            f"{Colors.RED}Error al cargar el historial: {e}. Empezando chat nuevo.{Colors.RESET}"
        )
        return None


# --- Configuración de la clave de API (sin cambios significativos aquí, solo el flujo general) ---
API_KEY = None
key_loaded_from_file = False
# ... (Toda la lógica de carga de API_KEY permanece igual que antes) ...
if os.path.exists(ENCRYPTED_API_KEY_FILE):
    print(
        f"{Colors.YELLOW}Se encontró un archivo de API Key encriptado ({ENCRYPTED_API_KEY_FILE}).{Colors.RESET}"
    )
    password_attempts = 0
    max_password_attempts = 3
    while password_attempts < max_password_attempts:
        password = getpass.getpass(
            f"{Colors.CYAN}Ingresa la contraseña para desencriptar la API Key (Enter para omitir): {Colors.RESET}"
        )
        if not password:
            print(
                f"{Colors.YELLOW}Omitiendo carga desde archivo encriptado.{Colors.RESET}"
            )
            break
        temp_api_key = load_decrypted_api_key(password)
        if temp_api_key:
            API_KEY = temp_api_key
            key_loaded_from_file = True
            print(
                f"{Colors.GREEN}API Key cargada y desencriptada exitosamente desde el archivo.{Colors.RESET}"
            )
            break
        else:
            password_attempts += 1
            print(
                f"{Colors.RED}Contraseña incorrecta o archivo corrupto.{Colors.RESET}"
            )
            if password_attempts < max_password_attempts:
                print(
                    f"{Colors.YELLOW}Intento {password_attempts + 1} de {max_password_attempts}.{Colors.RESET}"
                )
            else:
                print(
                    f"{Colors.RED}Demasiados intentos fallidos. No se pudo cargar la API Key desde el archivo encriptado.{Colors.RESET}"
                )
                delete_choice = (
                    input(
                        f"{Colors.YELLOW}¿Deseas eliminar el archivo de API Key encriptado ({ENCRYPTED_API_KEY_FILE}) debido a fallos? (s/N): {Colors.RESET}"
                    )
                    .strip()
                    .lower()
                )
                if delete_choice == "s":
                    try:
                        os.remove(ENCRYPTED_API_KEY_FILE)
                        print(
                            f"{Colors.GREEN}Archivo {ENCRYPTED_API_KEY_FILE} eliminado.{Colors.RESET}"
                        )
                    except Exception as e:
                        print(
                            f"{Colors.RED}No se pudo eliminar el archivo: {e}{Colors.RESET}"
                        )
                break

if API_KEY is None and os.path.exists(UNENCRYPTED_API_KEY_FILE):
    print(
        f"{Colors.YELLOW}Intentando cargar desde archivo de API Key sin encriptar ({UNENCRYPTED_API_KEY_FILE}).{Colors.RESET}"
    )
    temp_api_key = load_unencrypted_api_key()
    if temp_api_key:
        API_KEY = temp_api_key
        key_loaded_from_file = True
        print(
            f"{Colors.GREEN}API Key cargada exitosamente desde el archivo (sin encriptar).{Colors.RESET}"
        )
    elif os.path.exists(
        UNENCRYPTED_API_KEY_FILE
    ):  # Si la carga falló pero el archivo existe (ej. vacío o error de lectura)
        delete_choice = (
            input(
                f"{Colors.YELLOW}El archivo de API Key sin encriptar ({UNENCRYPTED_API_KEY_FILE}) no pudo ser leído correctamente o está vacío. ¿Deseas eliminarlo? (s/N): {Colors.RESET}"
            )
            .strip()
            .lower()
        )
        if delete_choice == "s":
            try:
                os.remove(UNENCRYPTED_API_KEY_FILE)
                print(
                    f"{Colors.GREEN}Archivo {UNENCRYPTED_API_KEY_FILE} eliminado.{Colors.RESET}"
                )
            except Exception as e:
                print(f"{Colors.RED}No se pudo eliminar el archivo: {e}{Colors.RESET}")

# 3. Si no se cargó desde ningún archivo, intentar desde variable de entorno
if API_KEY is None:
    API_KEY = os.getenv("GOOGLE_API_KEY")
    if API_KEY:
        print(
            f"{Colors.GREEN}API Key cargada desde la variable de entorno GOOGLE_API_KEY.{Colors.RESET}"
        )
    else:
        # 4. Si aún no hay clave, pedir al usuario que la ingrese.
        print(
            f"{Colors.YELLOW}La clave de API no se encontró en archivos locales ni en la variable de entorno GOOGLE_API_KEY.{Colors.RESET}"
        )
        print(
            f"{Colors.YELLOW}Puedes configurar la variable de entorno GOOGLE_API_KEY o crear un archivo '.gemini_api_key_encrypted'.{Colors.RESET}"
        )
        print(
            f"{Colors.YELLOW}Alternativamente, puedes ingresarla directamente ahora:{Colors.RESET}"
        )

        API_KEY = input(
            f"{Colors.CYAN}Por favor, ingresa tu clave de API de Gemini: {Colors.RESET}"
        ).strip()
        if not API_KEY:
            print(
                f"{Colors.RED}Error: No se ingresó ninguna clave de API.{Colors.RESET}"
            )
            sys.exit(1)

# 5. Si la API_KEY se obtuvo (y no fue de un archivo local), ofrecer guardarla.
if API_KEY and not key_loaded_from_file:
    print(
        f"\n{Colors.CYAN}¿Cómo deseas guardar esta API Key para futuros usos?{Colors.RESET}"
    )
    print(f"  {Colors.CYAN}1. Encriptada (recomendado){Colors.RESET}")
    print(
        f"  {Colors.CYAN}2. Sin encriptar ({Colors.RED}NO RECOMENDADO - RIESGO DE SEGURIDAD{Colors.CYAN}){Colors.RESET}"
    )
    print(f"  {Colors.CYAN}3. No guardar{Colors.RESET}")
    save_choice_input = input(
        f"{Colors.CYAN}Elige una opción (1/2/3, Enter para no guardar): {Colors.RESET}"
    ).strip()

    if save_choice_input == "1":
        while True:
            password = getpass.getpass(
                f"{Colors.CYAN}Ingresa una contraseña para encriptar la API Key (mínimo 8 caracteres, dejar en blanco para cancelar): {Colors.RESET}"
            )
            if not password:
                print(f"{Colors.YELLOW}Guardado encriptado cancelado.{Colors.RESET}")
                break
            if len(password) < 8:
                print(
                    f"{Colors.RED}La contraseña debe tener al menos 8 caracteres.{Colors.RESET}"
                )
                continue
            password_confirm = getpass.getpass(
                f"{Colors.CYAN}Confirma la contraseña: {Colors.RESET}"
            )
            if password == password_confirm:
                save_encrypted_api_key(API_KEY, password)
                break
            else:
                print(
                    f"{Colors.RED}Las contraseñas no coinciden. Inténtalo de nuevo.{Colors.RESET}"
                )
    elif save_choice_input == "2":
        save_unencrypted_api_key(API_KEY)
    elif save_choice_input == "3" or not save_choice_input:
        print(f"{Colors.YELLOW}API Key no guardada localmente.{Colors.RESET}")
    else:
        print(
            f"{Colors.YELLOW}Opción inválida. API Key no guardada localmente.{Colors.RESET}"
        )

# 6. Verificación final y configuración de la API
if not API_KEY:
    print(
        f"{Colors.RED}Error: No se pudo obtener la API Key por ningún método. Saliendo.{Colors.RESET}"
    )
    sys.exit(1)

try:
    genai.configure(api_key=API_KEY)
    print(f"\n{Colors.GREEN}API de Gemini configurada correctamente.{Colors.RESET}")
    time.sleep(0.5)
except Exception as e:
    print(
        f"{Colors.RED}Error al configurar la API con la clave proporcionada: {e}{Colors.RESET}"
    )
    print(f"{Colors.RED}Verifica que la clave de API sea correcta.{Colors.RESET}")
    sys.exit(1)

# --- Selección de Modelo (Modificado) ---
print(
    f"\n{Colors.BOLD}{Colors.BLUE}--- Selección de Modelo de Gemini ---{Colors.RESET}"
)
all_models_list = []
available_for_generation = []
# available_for_embedding = [] # Descomentar si se usan modelos de embedding
# other_models = []            # Descomentar si se usan otros modelos

try:
    all_models_list = list(genai.list_models())
    for m in all_models_list:
        if "generateContent" in m.supported_generation_methods:
            available_for_generation.append(m)
        # elif 'embedContent' in m.supported_generation_methods: # Descomentar si es necesario
        #     available_for_embedding.append(m)
        # else:
        #     other_models.append(m)

    if not available_for_generation:
        print(
            f"{Colors.RED}No se encontraron modelos disponibles para generación de contenido.{Colors.RESET}"
        )
        sys.exit(1)

    def model_sort_key(model_obj):
        name = model_obj.name  # El nombre es algo como 'models/gemini-1.5-pro-latest'
        # Extraer el nombre real del modelo para la ordenación
        actual_name_part = name.split("/")[-1]

        latest_score = 1 if "latest" in actual_name_part.lower() else 0
        pro_score = 1 if "pro" in actual_name_part.lower() else 0
        flash_score = 1 if "flash" in actual_name_part.lower() else 0
        # Para versiones como gemini-1.0-pro, gemini-1.5-pro.
        # Buscamos patrones como X.Y o solo X (ej. 1.5, 1.0, 1)
        version_match = re.search(r"(\d+)(?:[.\-_](\d+))?", actual_name_part)
        v_major, v_minor = 0, 0
        if version_match:
            v_major = int(version_match.group(1))
            if version_match.group(2):
                v_minor = int(version_match.group(2))

        # Prioridad: latest > pro > flash > mayor versión > menor versión > nombre alfabético
        return (
            -latest_score,  # Puntuaciones más altas primero (por eso el negativo)
            -pro_score,
            -flash_score,
            -v_major,
            -v_minor,
            actual_name_part,  # Orden alfabético como último recurso
        )

    available_for_generation.sort(key=model_sort_key)

    # Cargar el último modelo usado desde las preferencias
    preferences = load_preferences()
    last_used_model_name = preferences.get("last_used_model")
    DEFAULT_MODEL_NAME = None

    if last_used_model_name:
        # Verificar si el último modelo usado sigue disponible
        for m_obj in available_for_generation:
            if m_obj.name == last_used_model_name:
                DEFAULT_MODEL_NAME = last_used_model_name
                # Moverlo al principio de la lista para que sea la opción 0 (o 1 para el usuario)
                # y también el default si el usuario presiona Enter
                idx = available_for_generation.index(m_obj)
                m = available_for_generation.pop(idx)
                available_for_generation.insert(0, m)
                print(
                    f"{Colors.YELLOW}Último modelo usado: {DEFAULT_MODEL_NAME}{Colors.RESET}"
                )
                break
        if not DEFAULT_MODEL_NAME:
            print(
                f"{Colors.YELLOW}El último modelo usado ({last_used_model_name}) ya no está disponible o es inválido.{Colors.RESET}"
            )

    if (
        not DEFAULT_MODEL_NAME and available_for_generation
    ):  # Si no se cargó o no es válido el último usado
        DEFAULT_MODEL_NAME = available_for_generation[0].name

    print(
        f"\n{Colors.BOLD}Modelos disponibles para Generación de Contenido:{Colors.RESET}"
    )
    print(f"{Colors.BOLD}Selecciona uno por número para chatear:{Colors.RESET}")
    for i, m in enumerate(available_for_generation):
        default_indicator = ""
        if m.name == DEFAULT_MODEL_NAME and m.name == last_used_model_name:
            default_indicator = (
                f" ({Colors.GREEN}Por defecto - Último usado{Colors.RESET})"
            )
        elif m.name == DEFAULT_MODEL_NAME:
            default_indicator = f" ({Colors.GREEN}Por defecto{Colors.RESET})"
        elif (
            m.name == last_used_model_name
        ):  # Ya no es el default general, pero fue el último usado
            default_indicator = f" ({Colors.YELLOW}Último usado{Colors.RESET})"

        print(f"{Colors.YELLOW}{i + 1}.{Colors.RESET} {m.name}{default_indicator}")

    if DEFAULT_MODEL_NAME:
        print(
            f"\n({Colors.GREEN}Presiona Enter para usar el modelo por defecto:{Colors.RESET} {DEFAULT_MODEL_NAME})"
        )
    else:  # No debería ocurrir si available_for_generation tiene elementos
        print(f"{Colors.RED}No hay modelo por defecto configurado.{Colors.RESET}")


except Exception as e:
    print(f"{Colors.RED}Error al listar o procesar modelos: {e}{Colors.RESET}")
    print(
        f"{Colors.RED}Asegúrate de que tu clave de API es correcta y tienes conexión a internet.{Colors.RESET}"
    )
    sys.exit(1)

if not available_for_generation:  # Doble chequeo por si acaso
    print(
        f"{Colors.RED}No se puede seleccionar un modelo para generación ya que no hay disponibles.{Colors.RESET}"
    )
    sys.exit(1)

MODEL_NAME = None
while True:
    prompt_text = f"{Colors.CYAN}Ingresa el número del modelo para chatear"
    if DEFAULT_MODEL_NAME:
        prompt_text += f" o presiona Enter para usar ({DEFAULT_MODEL_NAME})"
    prompt_text += f": {Colors.RESET}"
    user_input_model_choice = input(prompt_text).strip()

    if not user_input_model_choice and DEFAULT_MODEL_NAME:
        MODEL_NAME = DEFAULT_MODEL_NAME
        print(f"{Colors.GREEN}Usando modelo por defecto:{Colors.RESET} {MODEL_NAME}")
        break
    elif user_input_model_choice:
        try:
            selected_index = int(user_input_model_choice) - 1
            if 0 <= selected_index < len(available_for_generation):
                MODEL_NAME = available_for_generation[selected_index].name
                print(f"{Colors.GREEN}Modelo seleccionado:{Colors.RESET} {MODEL_NAME}")
                break
            else:
                print(
                    f"{Colors.RED}Número fuera de rango. Por favor, ingresa un número válido.{Colors.RESET}"
                )
        except ValueError:
            print(
                f"{Colors.RED}Entrada inválida. Por favor, ingrese un número o presiona Enter.{Colors.RESET}"
            )
    elif (
        not DEFAULT_MODEL_NAME
    ):  # Si no hay modelo por defecto y el usuario no ingresó nada
        print(
            f"{Colors.RED}No hay modelo por defecto disponible. Por favor, selecciona un número de la lista.{Colors.RESET}"
        )

# Guardar el modelo seleccionado como el último usado
if MODEL_NAME:
    preferences["last_used_model"] = MODEL_NAME
    save_preferences(preferences)

time.sleep(0.5)

# --- BUCLE DE CHAT PRINCIPAL (la lógica interna del bucle permanece igual) ---
if MODEL_NAME:
    print(f"\n{Colors.GREEN}Iniciando chat con el modelo '{MODEL_NAME}'.{Colors.RESET}")
    print(
        f"{Colors.YELLOW}Escribe 'salir', 'exit' o 'quit' para terminar.{Colors.RESET}"
    )

    history_filename = get_chat_history_filename(MODEL_NAME)
    initial_history = []

    load_hist_choice = (
        input(
            f"{Colors.CYAN}¿Deseas cargar el historial anterior para este modelo ({history_filename})? (S/n): {Colors.RESET}"
        )
        .strip()
        .lower()
    )
    if load_hist_choice == "" or load_hist_choice == "s":
        loaded_history = load_chat_history(history_filename)
        if loaded_history:
            initial_history = loaded_history
    else:
        print(f"{Colors.YELLOW}Empezando una nueva sesión de chat.{Colors.RESET}")

    try:
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        }
        model = genai.GenerativeModel(MODEL_NAME, safety_settings=safety_settings)
        chat = model.start_chat(history=initial_history)

        while True:
            print(f"{Colors.BOLD}{Colors.CYAN}Tú: {Colors.RESET}", end="")
            user_input = ""
            try:
                user_input = input().strip()
            except KeyboardInterrupt:  # Manejar Ctrl+C para salir limpiamente
                print(f"\n{Colors.YELLOW}Saliendo del chat...{Colors.RESET}")
                break  # Sale del bucle de chat

            if user_input.lower() in ["salir", "exit", "quit"]:
                break
            if not user_input:
                continue

            print(
                f"{Colors.BOLD}{Colors.MAGENTA}{MODEL_NAME.split('/')[-1]}: {Colors.RESET}",
                end="",
            )  # Mostrar nombre corto del modelo
            try:
                response = chat.send_message(user_input, stream=True)
                # full_response_text = "" # No es necesario si no se hace nada más con ella inmediatamente
                for chunk in response:
                    if hasattr(chunk, "text"):
                        print(chunk.text, end="", flush=True)
                        # full_response_text += chunk.text
                    if chunk.prompt_feedback and chunk.prompt_feedback.block_reason:
                        print(
                            f"\n{Colors.RED}Tu prompt fue bloqueado: {chunk.prompt_feedback.block_reason_message}{Colors.RESET}"
                        )
                        break
                print()
            except Exception as e:
                print(
                    f"\n{Colors.RED}Error al enviar mensaje o recibir respuesta: {e}{Colors.RESET}"
                )
                continue

        save_hist_choice = (
            input(
                f"{Colors.CYAN}¿Deseas guardar el historial de esta sesión en '{history_filename}'? (S/n): {Colors.RESET}"
            )
            .strip()
            .lower()
        )
        if save_hist_choice == "" or save_hist_choice == "s":
            save_chat_history(chat, history_filename)

    except Exception as e:
        print(
            f"{Colors.RED}Ocurrió un error inesperado durante el chat: {e}{Colors.RESET}"
        )
        print(f"{Colors.RED}El chat ha terminado.{Colors.RESET}")
else:
    print(f"{Colors.RED}No se seleccionó ningún modelo. Saliendo.{Colors.RESET}")

print(f"\n{Colors.BOLD}{Colors.BLUE}--- Script finalizado ---{Colors.RESET}")


def run_chatbot():
    # --- Configuración de la clave de API ---
    API_KEY = None
    key_loaded_from_file = False
    # ... (TODA la lógica que tenías desde la carga de API_KEY hasta el print final del script) ...
    # ... Asegúrate de que las variables globales como ENCRYPTED_API_KEY_FILE, Colors, etc.
    # ... sean accesibles dentro de esta función, o pásalas como argumentos si es necesario.
    # ... Por cómo está estructurado tu script actual, las variables globales definidas
    # ... al inicio del script deberían ser accesibles.

    # Aquí va la lógica de carga de API_KEY, selección de modelo, bucle de chat, etc.
    # Por ejemplo:
    if os.path.exists(ENCRYPTED_API_KEY_FILE):
        print(
            f"{Colors.YELLOW}Se encontró un archivo de API Key encriptado ({ENCRYPTED_API_KEY_FILE}).{Colors.RESET}"
        )
        # ... y así sucesivamente ...

    # ... hasta el último print ...
    print(f"\n{Colors.BOLD}{Colors.BLUE}--- Script finalizado ---{Colors.RESET}")


if __name__ == "__main__":
    run_chatbot()

##<PyGemAi.py>
##Copyright (C) <2025> <Julio Cèsar Martìnez> <julioglez@gmail.com>
##
##This program is free software: you can redistribute it and/or modify
##it under the terms of the GNU General Public License as published by
##the Free Software Foundation, either version 3 of the License, or
##(at your option) any later version.
##This program is distributed in the hope that it will be useful,
##but WITHOUT ANY WARRANTY; without even the implied warranty of
##MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##GNU General Public License for more details.
##You should have received a copy of the GNU General Public License
##along with this program.  If not, see <https://www.gnu.org/licenses/>.
