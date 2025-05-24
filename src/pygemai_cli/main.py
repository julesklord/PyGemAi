import os
import re
import sys
import time
import getpass
import threading
import itertools
import shutil
import json
import google.generativeai as genai # Importa el módulo principal de genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold # Importa los tipos específicos
from typing import Optional, List, Dict # Añadido para compatibilidad de tipos

try:
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.backends import default_backend
    from cryptography.fernet import Fernet, InvalidToken
    import base64
except ImportError:
    # Direct print, as theme manager isn't available yet.
    print("\033[91m¡Houston, tenemos un problema! Falta 'cryptography'. "  # noqa: E501
          "Sin ella, tus secretos no están a salvo. Instálala con: "
          "pip install cryptography\033[0m")
    sys.exit(1)


class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    # Base colors for themes that might want to refer to them
    BASE_RED = "\033[91m"
    BASE_GREEN = "\033[92m"
    BASE_YELLOW = "\033[93m"
    BASE_BLUE = "\033[94m"
    BASE_MAGENTA = "\033[95m"
    BASE_CYAN = "\033[96m"
    BASE_WHITE = "\033[97m"


# --- Constantes ---
ENCRYPTED_API_KEY_FILE = ".gemini_api_key_encrypted"  # noqa: E501
UNENCRYPTED_API_KEY_FILE = ".gemini_api_key_unencrypted"  # noqa: E501
PREFERENCES_FILE = ".gemini_chatbot_prefs.json"
PROFILES_FILE = "pygemai_profiles.json"
SALT_SIZE = 16
ITERATIONS = 390_000


# --- Color Theme Definitions ---
PREDEFINED_THEMES = {
    "Legacy": {
        "colors": {
            "prompt_user": Colors.BOLD + Colors.BASE_CYAN,
            "prompt_model_name": Colors.BOLD + Colors.BASE_MAGENTA,
            "response_text": "", # Color base para la respuesta, usado por format_gemini_output
            "thinking_message": Colors.BASE_GREEN, # Para la animación de "pensando"
            "error_message": Colors.BASE_RED,
            "warning_message": Colors.BASE_YELLOW,
            "info_message": Colors.BASE_GREEN,
            "welcome_message_art": Colors.BOLD + Colors.BASE_CYAN,
            "welcome_message_text": Colors.BOLD + Colors.BASE_GREEN,
            "welcome_message_dev": Colors.BASE_YELLOW,
            "welcome_message_changes_title": Colors.BOLD + Colors.BASE_MAGENTA,  # noqa: E501
            "welcome_message_changes_item_bullet": Colors.BASE_YELLOW,
            "welcome_message_changes_item_text": "",
            "section_header": Colors.BOLD + Colors.BASE_BLUE,
            "list_item_bullet": Colors.BASE_YELLOW,
            "list_item_text": "",
            "inline_code": Colors.BASE_MAGENTA,
            "code_block_lang": Colors.BASE_YELLOW,
            "code_block_content": Colors.BASE_CYAN,
            "markdown_h1": Colors.BOLD + Colors.BASE_BLUE,
            "markdown_h2": Colors.BOLD + Colors.BASE_CYAN,
            "markdown_h3": Colors.BOLD + Colors.BASE_GREEN,
            "markdown_bold": Colors.BOLD,
            "markdown_italic_underline": Colors.UNDERLINE,
        }
    },
    "DefaultDark": {
        "colors": {
            "prompt_user": Colors.BOLD + "\033[38;5;81m",  # Darker Cyan/Blue
            "prompt_model_name": Colors.BOLD + "\033[38;5;208m",  # Orange
            "response_text": "\033[38;5;229m",  # Light Grey/Almost White for response_text
            "thinking_message": "\033[38;5;245m", # Un gris claro para "pensando"
            "error_message": Colors.BOLD + "\033[38;5;196m",  # Bright Red
            "warning_message": "\033[38;5;220m",  # Bright Yellow
            "info_message": "\033[38;5;113m",  # Light Green/Turquoise
            "welcome_message_art": Colors.BOLD + "\033[38;5;81m",
            "welcome_message_text": Colors.BOLD + "\033[38;5;153m", # Light Purple
            "welcome_message_dev": "\033[38;5;208m",
            "welcome_message_changes_title": Colors.BOLD + "\033[38;5;190m",  # Light Pink/Purple
            "welcome_message_changes_item_bullet": "\033[38;5;81m",
            "welcome_message_changes_item_text": "\033[38;5;229m",
            "section_header": Colors.BOLD + "\033[38;5;153m",
            "list_item_bullet": "\033[38;5;81m",
            "list_item_text": "\033[38;5;229m",
            "inline_code": "\033[38;5;180m",  # Light Purple/Pink
            "code_block_lang": "\033[38;5;214m",  # Light Orange
            "code_block_content": "\033[38;5;113m",
            "markdown_h1": Colors.BOLD + "\033[38;5;81m",
            "markdown_h2": Colors.BOLD + "\033[38;5;117m",  # Bright Blue
            "markdown_h3": Colors.BOLD + "\033[38;5;153m",
            "markdown_bold": Colors.BOLD,
            "markdown_italic_underline": Colors.UNDERLINE + "\033[38;5;220m",
        }
    }
}


class ThemeManager:
    def __init__(self, available_themes: dict, default_theme_name: str = "Legacy"):
        self.available_themes = available_themes
        self.default_theme_name = default_theme_name
        self.active_theme_name = default_theme_name

        if default_theme_name not in available_themes:
            if available_themes:
                self.default_theme_name = list(available_themes.keys())[0]
                self.active_theme_name = self.default_theme_name
                print(
                    f"{Colors.BASE_YELLOW}Advertencia: Tema por defecto '{default_theme_name}' "  # noqa: E501
                    f"no encontrado. Usando '{self.active_theme_name}'.{Colors.RESET}"
                )
            else:
                print(
                    f"{Colors.BASE_RED}Error: No hay temas definidos. La coloración no funcionará.{Colors.RESET}"  # noqa: E501
                )
                self.active_theme_colors = {}
                return
        self.active_theme_colors = available_themes[self.active_theme_name].get("colors", {})  # noqa: E501

    def set_active_theme(self, theme_name: str):
        if theme_name in self.available_themes:
            self.active_theme_name = theme_name
            self.active_theme_colors = self.available_themes[theme_name].get("colors", {})  # noqa: E501
        else:
            print(
                f"{Colors.BASE_YELLOW}Advertencia: Tema '{theme_name}' no encontrado. "  # noqa: E501
                f"Usando tema por defecto '{self.default_theme_name}'.{Colors.RESET}"
            )
            self.active_theme_name = self.default_theme_name
            if self.default_theme_name in self.available_themes:
                self.active_theme_colors = self.available_themes[self.default_theme_name].get("colors", {})  # noqa: E501
            else:
                self.active_theme_colors = {}

    def get_color(self, element_key: str) -> str:
        return self.active_theme_colors.get(element_key, "")

    def style(self, element_key: str, text: str, apply_reset: bool = True) -> str:
        color_code = self.get_color(element_key)
        is_bold_style = element_key == "markdown_bold" and color_code == Colors.BOLD
        is_underline_style = element_key == "markdown_italic_underline" and Colors.UNDERLINE in color_code  # noqa: E501

        if color_code:
            if (is_bold_style or is_underline_style) and not text.strip():
                return text
            reset_code = Colors.RESET if apply_reset else ""
            return f"{color_code}{text}{reset_code}"
        else:
            return text


# --- Funciones de Perfiles de Chat ---


def _parse_safety_settings(profile_settings: dict, theme_manager: ThemeManager) -> dict:
    parsed_settings = {}
    harm_category_map = { # Ahora HarmCategory está disponible globalmente
        "HARM_CATEGORY_HARASSMENT": HarmCategory.HARM_CATEGORY_HARASSMENT,
        "HARM_CATEGORY_HATE_SPEECH": HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        "HARM_CATEGORY_SEXUALLY_EXPLICIT": HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        "HARM_CATEGORY_DANGEROUS_CONTENT": HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
    }
    harm_block_threshold_map = {
        "BLOCK_NONE": HarmBlockThreshold.BLOCK_NONE,
        "BLOCK_ONLY_HIGH": HarmBlockThreshold.BLOCK_ONLY_HIGH,
        "BLOCK_MEDIUM_AND_ABOVE": HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
        "BLOCK_LOW_AND_ABOVE": HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
    }
    for key, value_str in profile_settings.items():
        category_enum = harm_category_map.get(key)
        threshold_enum = harm_block_threshold_map.get(value_str)
        if category_enum and threshold_enum:
            parsed_settings[category_enum] = threshold_enum
        else:
            print(theme_manager.style("warning_message",
                  f"Advertencia: Configuración de seguridad desconocida '{key}: {value_str}' en el perfil. Se omitirá."))
    return parsed_settings


def load_profiles(theme_manager: ThemeManager) -> list:
    if not os.path.exists(PROFILES_FILE):
        return []
    try:
        with open(PROFILES_FILE, "r", encoding="utf-8") as f:
            profiles = json.load(f)
            if not isinstance(profiles, list):
                print(theme_manager.style("error_message",
                      f"Error: El archivo de perfiles no contiene una lista. ({PROFILES_FILE})"))
                return []
            return profiles
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print(theme_manager.style("error_message",
              f"Error: El archivo de perfiles ({PROFILES_FILE}) está corrupto o no es un JSON válido."))
        return []
    except Exception as e:
        print(theme_manager.style("error_message",
              f"Error inesperado al cargar perfiles desde {PROFILES_FILE}: {e}"))
        return []


def save_profiles(profiles: list, theme_manager: ThemeManager):
    try:
        with open(PROFILES_FILE, "w", encoding="utf-8") as f:
            json.dump(profiles, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(theme_manager.style("error_message", f"Error al guardar perfiles en {PROFILES_FILE}: {e}"))


# --- Funciones de Encriptación/Desencriptación ---


def _derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITERATIONS, backend=default_backend())
    return base64.urlsafe_b64encode(kdf.derive(password.encode()))


def save_encrypted_api_key(api_key: str, password: str, theme_manager: ThemeManager):
    try:
        salt = os.urandom(SALT_SIZE)
        derived_key = _derive_key(password, salt)
        f = Fernet(derived_key)
        encrypted_api_key = f.encrypt(api_key.encode())
        with open(ENCRYPTED_API_KEY_FILE, "wb") as key_file:
            key_file.write(salt)
            key_file.write(encrypted_api_key)
        print(theme_manager.style("info_message", f"API Key encriptada y guardada en {ENCRYPTED_API_KEY_FILE}"))
        if os.name != "nt":
            os.chmod(ENCRYPTED_API_KEY_FILE, 0o600)
    except Exception as e:
        print(theme_manager.style("error_message", f"Error al guardar la API Key encriptada: {e}"))


def load_decrypted_api_key(password: str, theme_manager: ThemeManager) -> Optional[str]:
    if not os.path.exists(ENCRYPTED_API_KEY_FILE):
        return None
    try:
        with open(ENCRYPTED_API_KEY_FILE, "rb") as key_file:
            salt = key_file.read(SALT_SIZE)
            encrypted_api_key = key_file.read()
        derived_key = _derive_key(password, salt)
        f = Fernet(derived_key)
        return f.decrypt(encrypted_api_key).decode()
    except InvalidToken:
        return None  # Contraseña incorrecta o token inválido
    except Exception as e: # Captura otros errores como IOError, problemas de desencriptación, etc.
        print(theme_manager.style("error_message", f"Error al cargar o desencriptar la API Key: {e}"))
        return None


def save_unencrypted_api_key(api_key: str, theme_manager: ThemeManager):
    try:
        with open(UNENCRYPTED_API_KEY_FILE, "w") as key_file:
            key_file.write(api_key)
        warning_style_code = theme_manager.get_color("warning_message")
        print(f"{Colors.BOLD}{warning_style_code}ADVERTENCIA:{Colors.RESET}{warning_style_code} "
              f"API Key guardada SIN ENCRIPTAR en {UNENCRYPTED_API_KEY_FILE}.{Colors.RESET}")
        if os.name != "nt":
            os.chmod(UNENCRYPTED_API_KEY_FILE, 0o600)
    except Exception as e:
        print(theme_manager.style("error_message", f"Error al guardar la API Key sin encriptar: {e}"))


def load_unencrypted_api_key(theme_manager: ThemeManager) -> Optional[str]:
    if not os.path.exists(UNENCRYPTED_API_KEY_FILE):
        return None
    try:
        with open(UNENCRYPTED_API_KEY_FILE, "r") as key_file:
            api_key = key_file.read().strip()
            if api_key:
                warning_style_code = theme_manager.get_color("warning_message")
                print(f"{Colors.BOLD}{warning_style_code}ADVERTENCIA:{Colors.RESET}{warning_style_code} "
                      f"API Key cargada SIN ENCRIPTAR desde {UNENCRYPTED_API_KEY_FILE}.{Colors.RESET}")
                return api_key
            return None
    except Exception as e:
        print(theme_manager.style("error_message",
              f"Error al cargar la API Key desde el archivo sin encriptar: {e}"))
        return None


# --- Funciones de Preferencias ---


def save_preferences(prefs: dict, theme_manager: ThemeManager):
    try:
        with open(PREFERENCES_FILE, "w", encoding="utf-8") as f:
            json.dump(prefs, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(theme_manager.style("error_message", f"Error al guardar las preferencias: {e}"))


def load_preferences(theme_manager: ThemeManager) -> dict:
    if not os.path.exists(PREFERENCES_FILE):
        return {}
    try:
        with open(PREFERENCES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(theme_manager.style("error_message",
              f"Error al cargar las preferencias: {e}. Usando valores por defecto."))
        return {}


# --- Funciones de Historial de Chat ---


def get_chat_history_filename(model_name: str) -> str:
    safe_model_name = "".join(c if c.isalnum() or c in ("-", "_") else "_" for c in model_name)
    return f"chat_history_{safe_model_name}.json"


def save_chat_history(chat_session, filename: str, theme_manager: ThemeManager):
    history_to_save = [{'role': c.role, 'parts': [{'text': p.text} for p in c.parts if hasattr(p, "text")]}  # noqa: E501
                       for c in chat_session.history]
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(history_to_save, f, ensure_ascii=False, indent=2)
        print(theme_manager.style("info_message", f"Historial de chat guardado en {filename}"))
    except Exception as e:
        print(theme_manager.style("error_message", f"Error al guardar el historial: {e}"))


def load_chat_history(filename: str, theme_manager: ThemeManager) -> Optional[List]:
    if not os.path.exists(filename):
        return None
    try:
        with open(filename, "r", encoding="utf-8") as f:
            history = json.load(f)
        print(theme_manager.style("info_message", f"Historial de chat cargado desde {filename}"))
        return history
    except Exception as e:
        print(theme_manager.style("error_message", f"Error al cargar el historial: {e}. Empezando chat nuevo."))  # noqa: E501
        return None


# --- Funciones de Formateo de Salida ---


# --- Funciones de UI para Perfiles y Temas ---

def display_profiles(profiles: list, theme_manager: ThemeManager, show_details: bool = False,  # noqa: E501
                     current_profile_name: Optional[str] = None):
    """Muestra una lista numerada de perfiles."""
    if not profiles:
        print(theme_manager.style("warning_message", "No hay perfiles para mostrar."))
        return

    print(theme_manager.style("section_header", "\n--- Perfiles Disponibles ---"))
    for i, profile in enumerate(profiles):
        profile_name = profile.get("profile_name", f"Perfil {i + 1} (sin nombre)")
        model_id = profile.get("model_id", "No especificado")

        indicator = ""
        if current_profile_name and profile_name == current_profile_name:
            indicator = theme_manager.style("info_message", " (Actual)")

        profile_line = f"{i + 1}. {profile_name}"
        if show_details:
            profile_line += f" (Modelo: {model_id})"

        # Style the number and text separately
        num_styled = theme_manager.style("list_item_bullet", f"{i + 1}.")
        text_styled = theme_manager.style("list_item_text", f" {profile_name}{indicator}" +
                                          (f" (Modelo: {model_id})" if show_details else ""))
        print(num_styled + text_styled)

        if show_details:
            system_prompt = profile.get("system_prompt")
            if system_prompt:
                max_len = 60
                ellipsis = "..." if len(system_prompt) > max_len else ""
                print(theme_manager.style("list_item_text", f"    System Prompt: '{system_prompt[:max_len]}{ellipsis}'"))
            theme_name = profile.get("color_theme_name", "Legacy")
            print(theme_manager.style("list_item_text", f"    Tema: {theme_name}"))
            # Safety settings could be summarized here too if needed


def _get_predefined_safety_settings(level_name: str) -> Optional[Dict]:
    """Devuelve un diccionario de configuraciones de seguridad predefinidas."""
    # Estos son ejemplos, ajustar según necesidad
    levels = {
        "Default": None,  # Usará los defaults de genai.GenerativeModel
        "Lenient": {
            "HARM_CATEGORY_HARASSMENT": "BLOCK_NONE",
            "HARM_CATEGORY_HATE_SPEECH": "BLOCK_NONE",
            "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_ONLY_HIGH",
            "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_ONLY_HIGH",  # Mantener algo de bloqueo para contenido peligroso
        },
        "Balanced": {  # Similar a los defaults originales de PyGemAi
            "HARM_CATEGORY_HARASSMENT": "BLOCK_ONLY_HIGH",
            "HARM_CATEGORY_HATE_SPEECH": "BLOCK_ONLY_HIGH",
            "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_MEDIUM_AND_ABOVE",
            "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_ONLY_HIGH",
        },
        "Strict": {
            "HARM_CATEGORY_HARASSMENT": "BLOCK_MEDIUM_AND_ABOVE",
            "HARM_CATEGORY_HATE_SPEECH": "BLOCK_MEDIUM_AND_ABOVE",
            "HARM_CATEGORY_SEXUALLY_EXPLICIT": "BLOCK_MEDIUM_AND_ABOVE",
            "HARM_CATEGORY_DANGEROUS_CONTENT": "BLOCK_MEDIUM_AND_ABOVE",
        }
    }
    return levels.get(level_name)

# --- Fin Funciones UI para Perfiles y Temas ---


def create_profile_ui(theme_manager: ThemeManager) -> Optional[Dict]:
    """UI para crear un nuevo perfil de chat."""
    print(theme_manager.style("section_header", "\n--- Crear Nuevo Perfil ---"))

    new_profile = {}

    # 1. Nombre del Perfil
    while True:
        name = input(theme_manager.style("prompt_user", "Nombre del perfil: ")).strip()
        if name:
            # TODO: Add validation for unique profile name if profiles list is passed and checked
            new_profile["profile_name"] = name
            break
        else:
            print(theme_manager.style("error_message", "El nombre del perfil no puede estar vacío."))

    # 2. Selección de Modelo
    print(theme_manager.style("info_message", "\nSeleccionando modelo para el perfil..."))
    # This reuses parts of the model selection logic from run_chatbot's original form
    # It needs to be adapted or called carefully. For now, a simplified version:
    all_models_list = []
    available_for_generation = []
    try:
        all_models_list = list(genai.list_models())
        for m in all_models_list:
            if "generateContent" in m.supported_generation_methods:
                available_for_generation.append(m)
        if not available_for_generation:
            print(theme_manager.style("error_message", "No se encontraron modelos de IA para generación de contenido."))
            return None  # Cannot create profile without a model

        # Simplified sort for UI selection
        available_for_generation.sort(key=lambda m: m.name)

        print(theme_manager.style("info_message", "Modelos disponibles:"))
        for i, model in enumerate(available_for_generation):
            print(theme_manager.style("list_item_bullet", f"  {i + 1}. ") +
                  theme_manager.style("list_item_text", model.name))

        while True:
            try:
                choice = input(theme_manager.style("prompt_user", "Selecciona un modelo por número: ")).strip()
                model_idx = int(choice) - 1
                if 0 <= model_idx < len(available_for_generation):
                    new_profile["model_id"] = available_for_generation[model_idx].name
                    print(theme_manager.style("info_message", f"Modelo seleccionado: {new_profile['model_id']}"))
                    break
                else:
                    print(theme_manager.style("error_message", "Número fuera de rango."))
            except ValueError:
                print(theme_manager.style("error_message", "Entrada inválida. Ingresa un número."))
    except Exception as e:
        print(theme_manager.style("error_message", f"Error al listar modelos: {e}"))
        return None

    # 3. System Prompt (Opcional)
    sys_prompt = input(theme_manager.style("prompt_user", "\nSystem prompt (opcional, presiona Enter para omitir): ")).strip()
    if sys_prompt:
        new_profile["system_prompt"] = sys_prompt

    # 4. Selección de Tema de Color
    available_themes_names = list(PREDEFINED_THEMES.keys())
    print(theme_manager.style("info_message", "\nTemas de color disponibles:"))
    for i, theme_name_item in enumerate(available_themes_names):
        print(theme_manager.style("list_item_bullet", f"  {i + 1}. ") +
              theme_manager.style("list_item_text", theme_name_item))

    while True:
        try:
            choice = input(theme_manager.style("prompt_user", "Selecciona un tema por número (Enter para 'Legacy'): ")).strip()
            if not choice:  # Default to Legacy
                new_profile["color_theme_name"] = "Legacy"
                print(theme_manager.style("info_message", "Tema seleccionado: Legacy"))
                break
            theme_idx = int(choice) - 1
            if 0 <= theme_idx < len(available_themes_names):
                new_profile["color_theme_name"] = available_themes_names[theme_idx]
                print(theme_manager.style("info_message", f"Tema seleccionado: {new_profile['color_theme_name']}"))
                break
            else:
                print(theme_manager.style("error_message", "Número fuera de rango."))
        except ValueError:
            print(theme_manager.style("error_message", "Entrada inválida. Ingresa un número."))

    # 5. Selección de Nivel de Seguridad
    safety_levels = ["Default", "Lenient", "Balanced", "Strict"]
    print(theme_manager.style("info_message", "\nNiveles de seguridad predefinidos:"))
    for i, level_name in enumerate(safety_levels):
        print(theme_manager.style("list_item_bullet", f"  {i + 1}. ") +
              theme_manager.style("list_item_text", level_name))

    while True:
        try:
            choice = input(theme_manager.style("prompt_user", "Selecciona un nivel de seguridad (Enter para 'Default'): ")).strip()
            if not choice:  # Default to "Default"
                new_profile["safety_settings"] = _get_predefined_safety_settings("Default")  # Which is None
                print(theme_manager.style("info_message", "Nivel de seguridad: Default"))
                break
            level_idx = int(choice) - 1
            if 0 <= level_idx < len(safety_levels):
                selected_level_name = safety_levels[level_idx]
                new_profile["safety_settings"] = _get_predefined_safety_settings(selected_level_name)
                print(theme_manager.style("info_message", f"Nivel de seguridad seleccionado: {selected_level_name}"))
                break
            else:
                print(theme_manager.style("error_message", "Número fuera de rango."))
        except ValueError:
            print(theme_manager.style("error_message", "Entrada inválida. Ingresa un número."))

    print(theme_manager.style("info_message", f"\nPerfil '{new_profile['profile_name']}' creado."))
    return new_profile


def delete_profile_ui(profiles: list, theme_manager: ThemeManager) -> bool:
    """UI para eliminar un perfil existente."""
    if not profiles:
        print(theme_manager.style("warning_message", "No hay perfiles para eliminar."))
        return False

    print(theme_manager.style("section_header", "\n--- Eliminar Perfil ---"))
    display_profiles(profiles, theme_manager, show_details=False)

    try:
        choice_str = input(theme_manager.style("prompt_user",
                             "Ingresa el número del perfil a eliminar (o '0' para cancelar): ")).strip()
        choice = int(choice_str)

        if choice == 0:
            print(theme_manager.style("info_message", "Eliminación cancelada."))
            return False

        if 1 <= choice <= len(profiles):
            profile_to_delete = profiles[choice - 1]
            profile_name = profile_to_delete.get("profile_name", f"Perfil {choice}")

            confirm = input(theme_manager.style("warning_message",
                              f"¿Estás seguro de que quieres eliminar el perfil '{profile_name}'? (s/N): ")).strip().lower()

            if confirm == 's':
                deleted_profile = profiles.pop(choice - 1)
                save_profiles(profiles, theme_manager)  # Guardar la lista modificada
                print(theme_manager.style("info_message", f"Perfil '{deleted_profile.get('profile_name')}' eliminado."))
                return True
            else:
                print(theme_manager.style("info_message", "Eliminación cancelada."))
                return False
        else:
            print(theme_manager.style("error_message", "Número de perfil fuera de rango."))
            return False
    except ValueError:
        print(theme_manager.style("error_message", "Entrada inválida. Ingresa un número."))
        return False


def manage_profiles_ui(profiles: list, theme_manager: ThemeManager):
    """UI para gestionar perfiles (listar, crear, eliminar)."""
    while True:
        print(theme_manager.style("section_header", "\n--- Gestión de Perfiles ---"))
        print(theme_manager.style("list_item_bullet", "1. ") +
              theme_manager.style("list_item_text", "Listar Perfiles (Detallado)"))
        print(theme_manager.style("list_item_bullet", "2. ") +
              theme_manager.style("list_item_text", "Crear Nuevo Perfil"))
        print(theme_manager.style("list_item_bullet", "3. ") +
              theme_manager.style("list_item_text", "Eliminar Perfil"))
        print(theme_manager.style("list_item_bullet", "b. ") +
              theme_manager.style("list_item_text", "Volver a selección de perfil"))

        choice = input(theme_manager.style("prompt_user", "Selecciona una opción: ")).strip().lower()

        if choice == '1':
            display_profiles(profiles, theme_manager, show_details=True)
        elif choice == '2':
            new_profile = create_profile_ui(theme_manager)
            if new_profile:
                # Verificar si ya existe un perfil con el mismo nombre (case-insensitive)
                existing_profile_index = -1
                for i, p in enumerate(profiles):
                    if p.get("profile_name", "").lower() == new_profile.get("profile_name", "").lower():
                        existing_profile_index = i
                        break

                if existing_profile_index != -1:
                    overwrite = input(theme_manager.style("warning_message",
                                        f"Un perfil llamado '{new_profile['profile_name']}' "
                                        "ya existe. ¿Sobrescribir? (s/N): ")).strip().lower()
                    if overwrite == 's':
                        profiles[existing_profile_index] = new_profile
                        print(theme_manager.style("info_message", f"Perfil '{new_profile['profile_name']}' sobrescrito."))
                    else:
                        print(theme_manager.style("info_message", "Creación/actualización cancelada."))
                        continue  # Vuelve al menú de gestión
                else:
                    profiles.append(new_profile)

                save_profiles(profiles, theme_manager)
        elif choice == '3':
            delete_profile_ui(profiles, theme_manager)
        elif choice == 'b':
            print(theme_manager.style("info_message", "Volviendo a selección de perfil..."))
            break
        else:
            print(theme_manager.style("error_message", "Opción no válida."))


def process_standard_markdown(text: str, theme_manager: ThemeManager) -> str:
    text = re.sub(r"`(.*?)`", lambda m: theme_manager.style("inline_code", m.group(1)), text)
    text = re.sub(r"^### (.*)", lambda m: theme_manager.style("markdown_h3", m.group(1).strip()), text, flags=re.MULTILINE)
    text = re.sub(r"^## (.*)", lambda m: theme_manager.style("markdown_h2", m.group(1).strip()), text, flags=re.MULTILINE)
    text = re.sub(r"^# (.*)", lambda m: theme_manager.style("markdown_h1", m.group(1).strip()), text, flags=re.MULTILINE)
    text = re.sub(r"^(\s*)\* (.*)", lambda m: f"{m.group(1)}{theme_manager.get_color('list_item_bullet')}* {Colors.RESET}{theme_manager.style('list_item_text', m.group(2))}", text, flags=re.MULTILINE)
    text = re.sub(r"^(\s*)- (.*)", lambda m: f"{m.group(1)}{theme_manager.get_color('list_item_bullet')}- {Colors.RESET}{theme_manager.style('list_item_text', m.group(2))}", text, flags=re.MULTILINE)
    text = re.sub(r"^(\s*)(\d+\.) (.*)", lambda m: f"{m.group(1)}{theme_manager.get_color('list_item_bullet')}{m.group(2)} {Colors.RESET}{theme_manager.style('list_item_text', m.group(3))}", text, flags=re.MULTILINE)
    text = re.sub(r"\*\*(.*?)\*\*", lambda m: theme_manager.style("markdown_bold", m.group(1)), text)
    text = re.sub(r"\*([^*]+?)\*", lambda m: theme_manager.style("markdown_italic_underline", m.group(1)), text)
    text = re.sub(r"_(.+?)_", lambda m: theme_manager.style("markdown_italic_underline", m.group(1)), text)
    return text


def format_gemini_output(text: str, theme_manager: ThemeManager) -> str:
    processed_parts = []
    last_end = 0
    for match in re.finditer(r"```(\w*)\n?(.*?)```", text, flags=re.DOTALL):
        pre_match_text = text[last_end:match.start()]
        processed_parts.append(process_standard_markdown(pre_match_text, theme_manager))
        lang = match.group(1) or ""
        code_content = match.group(2).strip('\n')
        indented_code = "\n".join([f"  {line}" for line in code_content.split('\n')])
        lang_styled = theme_manager.style("code_block_lang", f"```{lang}", apply_reset=False)
        content_styled = theme_manager.style("code_block_content", indented_code)
        code_block_formatted = (f"{lang_styled}{Colors.RESET}\n{content_styled}\n"
                                f"{theme_manager.style('code_block_lang', '```')}")
        processed_parts.append(code_block_formatted)
        last_end = match.end()
    remaining_text = text[last_end:]
    processed_parts.append(process_standard_markdown(remaining_text, theme_manager))
    base_response_color = theme_manager.get_color("response_text")
    final_content = "".join(processed_parts)
    # Only apply base color if content is not empty and not already starting with an ANSI code from markdown
    if final_content.strip() and not final_content.startswith("\033["):
        return base_response_color + final_content + Colors.RESET if base_response_color else final_content
    return final_content  # Already colored or empty


# --- Animación de "Pensando" ---
THINKING_MESSAGES = [
    "Pensando...", "Thinking...", "Réflexion...", "Nachdenken...", "Meditando...",
    "Elaborando...", "考え中...", "思考中...", "Processando...", "Un momento...",
]
SPINNER_CHARS = itertools.cycle(['-', '\\', '|', '/'])
stop_animation_event = threading.Event()


def animate_thinking(theme_manager: ThemeManager, model_prompt_text: str):
    """
    Muestra una animación de 'pensando' en la consola.
    `model_prompt_text` debe ser el texto del prompt del modelo ya estilizado y SIN Colors.RESET al final.
    """
    message_cycler = itertools.cycle(THINKING_MESSAGES)
    current_message = next(message_cycler)
    message_display_counter = 0
    # Cambiar mensaje cada ~2 segundos (20 * 0.1s)
    MESSAGE_CHANGE_INTERVAL_TICKS = 20

    thinking_style_key = "thinking_message"
    if thinking_style_key not in theme_manager.active_theme_colors:
        thinking_style_key = "info_message" # Fallback

    terminal_width = shutil.get_terminal_size((80, 24)).columns

    while not stop_animation_event.is_set():
        if message_display_counter >= MESSAGE_CHANGE_INTERVAL_TICKS:
            current_message = next(message_cycler)
            message_display_counter = 0

        spinner_char = next(SPINNER_CHARS)
        thinking_msg_styled = theme_manager.style(thinking_style_key, f" {current_message} {spinner_char}", apply_reset=False)
        full_line = f"\r{model_prompt_text}{thinking_msg_styled}{Colors.RESET} "
        
        sys.stdout.write(full_line.ljust(terminal_width)[:terminal_width] + '\r') # Escribir y limpiar el resto de la línea
        sys.stdout.flush()
        message_display_counter += 1
        time.sleep(0.1)

    sys.stdout.write('\r' + ' ' * terminal_width + '\r') # Limpiar la línea completa al salir
    sys.stdout.flush()

# --- ¡Aquí empieza la fiesta! La función principal del chatbot ---
def display_welcome_message(theme_manager: ThemeManager):
    # Intenta importar __version__ de forma que funcione tanto si es un módulo del paquete
    # como si se ejecuta como script (después de ajustar sys.path).
    try:
        from pygemai_cli import __version__
    except ImportError:
        # Fallback si, por alguna razón, la importación absoluta falla
        # (esto no debería ocurrir si sys.path se ajusta correctamente al ejecutar como script)
        print(theme_manager.style("warning_message", "Advertencia: No se pudo determinar la versión del paquete."))
        __version__ = "desconocida"


    art_lines = f"""

PPPPPPP  YY    YY   GGGGGG   EEEEE   MMMMM      MMMMM     AAAAA      II 
PP    PP  YY  YY   GG        EE       MM MMM  MMM MM     AA   AA     
PP    PP   YYYY    GG   GGG  EEEEEEE  MM  MMMMMM  MM    AAAA AAAA    II
PPPPPPP     YY     GG    GG  EE       MM   MMMM   MM   AA  AAA  AA   II
PP          YY   ___GG__GG____EEEEE____M____MM____M__ A_A_______A_A__II____
PP          YY      ___________________________________________________________ 
__________________________________________________________________________________
Ahora con esteroides!  ______________________________________________________________
"""
    pygemai_art = theme_manager.style("welcome_message_art", art_lines.strip())
    welcome_text_raw = f"¡Bienvenido a PyGemAi v{__version__}!"
    developer_text_raw = "Un desarrollo de: julesklord(julioglez.93@gmail.com)"

    # Centering text after styling can be tricky due to invisible ANSI codes.
    # A simple approach is to center the raw text and then style it.
    centered_welcome = f"{welcome_text_raw:^80}"
    centered_developer = f"{developer_text_raw:^80}"

    print(pygemai_art)
    print(theme_manager.style("welcome_message_text", centered_welcome))
    print(theme_manager.style("welcome_message_dev", centered_developer))

    print(theme_manager.style("welcome_message_changes_title", "\n--- Novedades en esta versión ---"))
    changes_list = [
        f"✨ Gestión avanzada de {theme_manager.style('info_message', 'perfiles de chat')} y {theme_manager.style('info_message', 'temas de color')} personalizables.",
        f"🎨 ¡Formato {theme_manager.style('markdown_bold', 'Markdown')} mejorado en las respuestas del chat!",
        f"⏳ Animación de 'pensando' {theme_manager.style('info_message', 'mejorada')} para una mejor experiencia.",
        f"🔑 Flujo de guardado de API Key {theme_manager.style('info_message', 'optimizado')}."
    ]
    for change in changes_list:
        bullet = theme_manager.style("welcome_message_changes_item_bullet", "* ")
        text = theme_manager.style("welcome_message_changes_item_text", change)
        print(bullet + text)

    separator_line = "-" * 80
    print(theme_manager.style("section_header", f"\n{separator_line}"))
    time.sleep(1.5)


def run_chatbot():
    theme_manager = ThemeManager(PREDEFINED_THEMES, "Legacy")
    profiles_data = load_profiles(theme_manager)
    active_profile = None
    profile_model_id = None
    profile_safety_settings = None
    profile_system_prompt = None
    profile_name = "Default"  # Default profile name if none loaded

    if profiles_data:
        active_profile = profiles_data[0]
        profile_name = active_profile.get("profile_name", "Perfil Desconocido")
        profile_color_theme = active_profile.get("color_theme_name")
        if profile_color_theme:
            theme_manager.set_active_theme(profile_color_theme)

    display_welcome_message(theme_manager)

    if active_profile:
        print(theme_manager.style("info_message",
              f"Se cargaron {len(profiles_data)} perfil(es) de chat. Usando perfil: '{profile_name}'"))
        profile_model_id = active_profile.get("model_id")
        profile_safety_settings_data = active_profile.get("safety_settings")
        profile_system_prompt = active_profile.get("system_prompt")

        if profile_model_id:
            print(theme_manager.style("info_message",
                  f"Usando modelo '{profile_model_id}' del perfil activo '{profile_name}'."))
        if profile_safety_settings_data:
            print(theme_manager.style("info_message",
                  f"Aplicando configuraciones de seguridad del perfil activo '{profile_name}'."))
            profile_safety_settings = _parse_safety_settings(profile_safety_settings_data, theme_manager)
    else:
        print(theme_manager.style("warning_message",
              "No se encontraron perfiles de chat. Se usarán las configuraciones por defecto/manuales."))

    API_KEY = None
    key_loaded_from_file = False
    if os.path.exists(ENCRYPTED_API_KEY_FILE):
        print(theme_manager.style("info_message",
              f"Intentando cargar API Key desde archivo encriptado ({ENCRYPTED_API_KEY_FILE})."))
        password_attempts = 0
        max_password_attempts = 3
        while password_attempts < max_password_attempts:
            password = getpass.getpass(theme_manager.style("prompt_user",
                                       "Ingresa la contraseña para desencriptar la API Key (Enter para omitir): "))
            if not password:
                print(theme_manager.style("warning_message", "Omitiendo carga desde archivo encriptado."))
                break
            temp_api_key = load_decrypted_api_key(password, theme_manager)
            if temp_api_key:
                API_KEY = temp_api_key
                key_loaded_from_file = True
                print(theme_manager.style("info_message", "API Key cargada y desencriptada exitosamente."))
                break
            else:
                password_attempts += 1
                if password_attempts < max_password_attempts:
                    print(theme_manager.style("error_message", "Contraseña incorrecta o archivo corrupto."))
                else:
                    print(theme_manager.style("error_message", "Demasiados intentos fallidos."))
                    delete_choice = input(theme_manager.style("prompt_user",
                                          f"¿Deseas eliminar el archivo {ENCRYPTED_API_KEY_FILE}? (s/N): ")).strip().lower()
                    if delete_choice == 's':
                        try:
                            os.remove(ENCRYPTED_API_KEY_FILE)
                            print(theme_manager.style("info_message", f"Archivo {ENCRYPTED_API_KEY_FILE} eliminado."))
                        except Exception as e:
                            print(theme_manager.style("error_message", f"No se pudo eliminar el archivo: {e}"))
                    break

    if API_KEY is None and os.path.exists(UNENCRYPTED_API_KEY_FILE):
        temp_api_key = load_unencrypted_api_key(theme_manager)
        if temp_api_key:
            API_KEY = temp_api_key
            key_loaded_from_file = True
        elif os.path.exists(UNENCRYPTED_API_KEY_FILE):
            delete_choice = input(theme_manager.style("prompt_user",
                                  f"El archivo {UNENCRYPTED_API_KEY_FILE} no pudo ser leído o está vacío. "
                                  "¿Deseas eliminarlo? (s/N): ")).strip().lower()
            if delete_choice == 's':
                try:
                    os.remove(UNENCRYPTED_API_KEY_FILE)
                    print(theme_manager.style("info_message", f"Archivo {UNENCRYPTED_API_KEY_FILE} eliminado."))
                except Exception as e:
                    print(theme_manager.style("error_message", f"No se pudo eliminar el archivo: {e}"))

    if API_KEY is None:
        API_KEY = os.getenv("GOOGLE_API_KEY")
        if API_KEY:
            print(theme_manager.style("info_message", "API Key cargada desde la variable de entorno GOOGLE_API_KEY."))
        else:
            print(theme_manager.style("warning_message", "API Key no encontrada en archivos o variable de entorno."))
            API_KEY = input(theme_manager.style("prompt_user", "Por favor, ingresa tu clave de API de Gemini: ")).strip()
            if not API_KEY:
                print(theme_manager.style("error_message", "No se ingresó clave de API. Saliendo."))
                sys.exit(1)

    if API_KEY and not key_loaded_from_file:
        print(theme_manager.style("prompt_user", "\n¿Cómo deseas guardar esta API Key para futuros usos?"))
        print(theme_manager.style("prompt_user", "  1. Encriptada (recomendado)"))
        no_rec_text = theme_manager.style("error_message", "NO RECOMENDADO - RIESGO DE SEGURIDAD", apply_reset=False)  # Keep prompt color
        print(theme_manager.style("prompt_user", f"  2. Sin encriptar ({no_rec_text}{theme_manager.get_color('prompt_user')})"))
        print(theme_manager.style("prompt_user", "  3. No guardar"))
        save_choice_input = input(theme_manager.style("prompt_user", "Elige una opción (1/2/3, Enter para no guardar): ")).strip()
        if save_choice_input == "1":
            # ... (rest of API key saving logic using theme_manager for prints)
            while True:
                password = getpass.getpass(theme_manager.style("prompt_user",
                                           "Ingresa contraseña para encriptar (mín. 8 car., Enter para cancelar): "))
                if not password:
                    print(theme_manager.style("warning_message", "Guardado cancelado."))
                    break
                if len(password) < 8:
                    print(theme_manager.style("error_message", "Contraseña muy corta."))
                    continue
                password_confirm = getpass.getpass(theme_manager.style("prompt_user", "Confirma contraseña: "))
                if password == password_confirm:
                    save_encrypted_api_key(API_KEY, password, theme_manager)
                    break
                else:
                    print(theme_manager.style("error_message", "Las contraseñas no coinciden."))
        elif save_choice_input == "2":
            save_unencrypted_api_key(API_KEY, theme_manager)
        else:
            print(theme_manager.style("warning_message", "API Key no guardada localmente."))

    if not API_KEY:
        print(theme_manager.style("error_message", "No se pudo obtener la API Key. Saliendo."))
        sys.exit(1)

    try:
        genai.configure(api_key=API_KEY)
        print(theme_manager.style("info_message", "\nAPI de Gemini configurada correctamente."))
        time.sleep(0.5)
    except Exception as e:
        print(theme_manager.style("error_message", f"Error al configurar la API: {e}. Verifica la clave."))
        sys.exit(1)

    MODEL_NAME = None
    if profile_model_id:
        MODEL_NAME = profile_model_id
    else:
        print(theme_manager.style("section_header", "\n--- Selección de Modelo de Gemini ---"))
        available_for_generation = []
        try:
            all_models_list = list(genai.list_models())
            for m in all_models_list:
                if "generateContent" in m.supported_generation_methods:
                    available_for_generation.append(m)
            if not available_for_generation:
                print(theme_manager.style("error_message", "No se encontraron modelos para generación de contenido."))
                sys.exit(1)

            def model_sort_key(model_obj):
                name = model_obj.name
                actual_name_part = name.split("/")[-1]
                scores = (-1 if "latest" in actual_name_part else 0,
                          -1 if "pro" in actual_name_part else 0,
                          -1 if "flash" in actual_name_part else 0)
                version_match = re.search(r"(\d+)(?:[.\-_](\d+))?", actual_name_part)
                v_major, v_minor = (int(version_match.group(1)), int(version_match.group(2) or 0)) if version_match else (0, 0)
                return (*scores, -v_major, -v_minor, actual_name_part)
            available_for_generation.sort(key=model_sort_key)

            preferences = load_preferences(theme_manager)
            last_used_model_name = preferences.get("last_used_model")
            DEFAULT_MODEL_NAME = None
            if last_used_model_name:
                for i, m_obj in enumerate(available_for_generation):
                    if m_obj.name == last_used_model_name:
                        DEFAULT_MODEL_NAME = m_obj.name
                        m_pop = available_for_generation.pop(i)
                        available_for_generation.insert(0, m_pop)
                        print(theme_manager.style("info_message", f"Último modelo usado: {DEFAULT_MODEL_NAME}"))
                        break
                if not DEFAULT_MODEL_NAME:
                    print(theme_manager.style("warning_message", f"Último modelo ({last_used_model_name}) no disponible."))
            if not DEFAULT_MODEL_NAME and available_for_generation:
                DEFAULT_MODEL_NAME = available_for_generation[0].name

            print(theme_manager.style("info_message", "Selecciona un modelo por número:"))
            for i, m_enum in enumerate(available_for_generation):
                indicator = ""
                if m_enum.name == DEFAULT_MODEL_NAME:
                    indicator += theme_manager.style("info_message", " (Por defecto)")
                if m_enum.name == last_used_model_name and m_enum.name != DEFAULT_MODEL_NAME:
                    indicator += theme_manager.style("warning_message", " (Último usado)")
                print(f"{theme_manager.style('list_item_bullet', str(i + 1) + '.')} "
                      f"{theme_manager.style('list_item_text', m_enum.name)}{indicator}")

            if DEFAULT_MODEL_NAME:
                print(theme_manager.style("info_message", f"\n(Enter para usar por defecto: {DEFAULT_MODEL_NAME})"))
            else:
                print(theme_manager.style("error_message", "No hay modelo por defecto."))

            while True:
                choice_prompt = theme_manager.style("prompt_user", "Elige un modelo" +
                                                  (f" (Enter para {DEFAULT_MODEL_NAME})" if DEFAULT_MODEL_NAME else "") + ": ")
                user_input_model_choice = input(choice_prompt).strip()
                if not user_input_model_choice and DEFAULT_MODEL_NAME:
                    MODEL_NAME = DEFAULT_MODEL_NAME
                    break
                try:
                    idx = int(user_input_model_choice) - 1
                    if 0 <= idx < len(available_for_generation):
                        MODEL_NAME = available_for_generation[idx].name
                        break
                    else:
                        print(theme_manager.style("error_message", "Número fuera de rango."))
                except ValueError:
                    print(theme_manager.style("error_message", "Entrada inválida."))
            print(theme_manager.style("info_message", f"Modelo seleccionado: {MODEL_NAME}"))
            if MODEL_NAME and not profile_model_id:
                preferences["last_used_model"] = MODEL_NAME
                save_preferences(preferences, theme_manager)
        except Exception as e:
            print(theme_manager.style("error_message", f"Error al listar/seleccionar modelos: {e}"))
            sys.exit(1)

    if not MODEL_NAME:
        print(theme_manager.style("error_message", "No se seleccionó modelo. Saliendo."))
        sys.exit(1)

    print(theme_manager.style("info_message", f"\nIniciando chat con '{MODEL_NAME}'."))
    print(theme_manager.style("warning_message", "Escribe 'salir', 'exit' o 'quit' para terminar."))
    history_filename = get_chat_history_filename(MODEL_NAME)
    initial_history = []
    load_hist_choice = input(theme_manager.style("prompt_user",
                             f"¿Cargar historial para este modelo ({history_filename})? (S/n): ")).strip().lower()
    if load_hist_choice == "" or load_hist_choice == "s":
        loaded_history = load_chat_history(history_filename, theme_manager)
        if loaded_history:
            initial_history = loaded_history
    else:
        print(theme_manager.style("warning_message", "Empezando nueva sesión."))

    if profile_system_prompt and isinstance(profile_system_prompt, str) and profile_system_prompt.strip():
        max_len = 70
        ellipsis = "..." if len(profile_system_prompt) > max_len else ""
        print(theme_manager.style("info_message",
              f"Usando system prompt del perfil '{profile_name}': '{profile_system_prompt[:max_len]}{ellipsis}'"))
        system_prompt_content = {'role': 'user', 'parts': [{'text': profile_system_prompt.strip()}]}
        if not (initial_history and initial_history[0]['role'] == 'user' and
                initial_history[0]['parts'][0]['text'] == profile_system_prompt.strip()):
            initial_history.insert(0, system_prompt_content)

    try:
        safety_settings_to_use = profile_safety_settings or {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_ONLY_HIGH,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_ONLY_HIGH,
        }
        model = genai.GenerativeModel(MODEL_NAME, safety_settings=safety_settings_to_use)
        chat = model.start_chat(history=initial_history)

        while True:
            print(theme_manager.style("prompt_user", "Tú: "), end="")
            try:
                user_input = input().strip()
            except KeyboardInterrupt:
                print(theme_manager.style("warning_message", "\nSaliendo..."))
                break
            if user_input.lower() in ["salir", "exit", "quit"]:
                break
            if not user_input:
                continue

            model_name_for_prompt = MODEL_NAME.split('/')[-1]
            styled_model_name_prompt = theme_manager.style("prompt_model_name", f"{model_name_for_prompt}:", apply_reset=False)

            stop_animation_event.clear()
            animation_thread = threading.Thread(
                target=animate_thinking,
                args=(theme_manager, styled_model_name_prompt)
            )
            animation_thread.daemon = True # Permite salir aunque el hilo esté activo
            
            full_response_text_parts = []
            first_chunk_received = False
            error_during_stream = False

            try:
                animation_thread.start()
                response = chat.send_message(user_input, stream=True)

                for chunk in response:
                    if not first_chunk_received: # Al recibir el primer dato (texto o feedback)
                        stop_animation_event.set()
                        if animation_thread.is_alive():
                            animation_thread.join(timeout=0.5) # Esperar a que limpie
                        # Imprimir el prompt del modelo ahora que la animación terminó
                        sys.stdout.write(f"\r{styled_model_name_prompt}{Colors.RESET} ") # \r para asegurar inicio de línea
                        sys.stdout.flush()
                        first_chunk_received = True

                    if hasattr(chunk, "text") and chunk.text: # Asegurarse que hay texto
                        sys.stdout.write(chunk.text) # Salida progresiva del texto
                        sys.stdout.flush()
                        full_response_text_parts.append(chunk.text)

                    if chunk.prompt_feedback and chunk.prompt_feedback.block_reason:
                        if not stop_animation_event.is_set(): # Asegurar que la animación se detenga
                            stop_animation_event.set()
                            if animation_thread.is_alive():
                                animation_thread.join(timeout=0.5)
                        if not first_chunk_received: # Si el error es lo primero que llega
                             sys.stdout.write(f"\r{styled_model_name_prompt}{Colors.RESET} ")
                             sys.stdout.flush()
                        
                        sys.stdout.write("\n") # Nueva línea para el mensaje de error
                        # print() ya añade newline, \n en f-string es para asegurar que el mensaje de error esté en su propia línea
                        print(theme_manager.style("error_message", f"Prompt bloqueado: {chunk.prompt_feedback.block_reason_message}"))
                        full_response_text_parts.clear()
                        error_during_stream = True
                        break
                
                # Después del bucle de chunks
                if not stop_animation_event.is_set(): # Si el bucle terminó muy rápido o respuesta vacía
                    stop_animation_event.set()
                    if animation_thread.is_alive():
                        animation_thread.join(timeout=0.5)
                
                if not first_chunk_received and not error_during_stream:
                    # Respuesta vacía, sin errores. La animación se detuvo (o se detendrá).
                    # Imprimir el prompt del modelo.
                    sys.stdout.write(f"\r{styled_model_name_prompt}{Colors.RESET} ")
                    sys.stdout.flush()

                # Nueva línea después de la salida progresiva (o el prompt si no hubo salida)
                # Solo si no hubo un error que ya manejó su propia salida de línea.
                if not error_during_stream:
                    sys.stdout.write("\n")
                    sys.stdout.flush()

                # Ahora, si no hubo error y tenemos texto, lo formateamos y lo imprimimos.
                if not error_during_stream and full_response_text_parts:
                    final_text = "".join(full_response_text_parts)
                    if final_text.strip(): # Solo si hay contenido real
                        formatted_text = format_gemini_output(final_text, theme_manager)
                        sys.stdout.write(formatted_text) # Imprime el texto formateado
                        sys.stdout.write("\n") # Añade la nueva línea final para el turno de respuesta
                        sys.stdout.flush()
                
            except Exception as e:
                if not stop_animation_event.is_set():
                    stop_animation_event.set()
                if animation_thread.is_alive():
                    animation_thread.join(timeout=0.5)
                
                if not first_chunk_received: # Si el error ocurrió antes de imprimir el prompt del modelo
                    sys.stdout.write(f"\r{styled_model_name_prompt}{Colors.RESET} ")
                    sys.stdout.flush()
                print(theme_manager.style("error_message", f"\nError en comunicación con API: {e}"))
                full_response_text_parts.clear() # No guardar historial si hubo este error
                continue
    except Exception as e:
        print(theme_manager.style("error_message", f"Error inesperado en chat: {e}. Chat terminado."))

    if 'chat' in locals() and chat.history:
        save_hist_choice = input(theme_manager.style("prompt_user",
                                 f"¿Guardar historial en '{history_filename}'? (S/n): ")).strip().lower()
        if save_hist_choice == "" or save_hist_choice == "s":
            save_chat_history(chat, history_filename, theme_manager)

    print(theme_manager.style("section_header", "\n--- Script finalizado. ¡Hasta la próxima! ---"))


if __name__ == "__main__":
    # Si main.py se ejecuta directamente (ej. python src/pygemai_cli/main.py),
    # las importaciones relativas o las que dependen de que el paquete esté en sys.path fallarán.
    # Ajustamos sys.path para que el directorio 'src' (padre de 'pygemai_cli') esté accesible,
    # permitiendo así importaciones como 'from pygemai_cli import ...'.
    if __package__ is None: # True cuando se ejecuta como script y no con -m
        import os
        import sys
        # Ruta al directorio 'src/pygemai_cli'
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Ruta al directorio 'src'
        package_root = os.path.dirname(script_dir)
        if package_root not in sys.path:
            sys.path.insert(0, package_root)

    run_chatbot()

# <PyGemAi.py>
# Copyright (C) <2024> <Julio Cèsar Martìnez> <julioglez@gmail.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
