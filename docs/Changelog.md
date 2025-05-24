# Changelog - (PyGemAi) - Gemini API Call Script

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [1.2.1] - 2025-05-15

### Added
- **Advanced Chat Profile Management (`manage_profiles_ui`, `create_profile_ui`, `delete_profile_ui`, `display_profiles`, `load_profiles`, `save_profiles`):**
  - Creation, listing, and deletion of chat profiles.
  - Each profile can configure:
    - Profile name.
    - Specific AI model (e.g., `gemini-pro`, `gemini-1.5-flash-latest`).
    - Custom "system prompt" to guide model behavior.
    - Color theme for the interface (`ThemeManager`).
    - Content safety level (`_parse_safety_settings`, `_get_predefined_safety_settings`).
  - The active profile is loaded at startup, and its settings (model, theme, etc.) are applied automatically.
- **Customizable Color Themes (`ThemeManager`, `PREDEFINED_THEMES`):**
  - Introduction of a theme system for the command-line interface.
  - Predefined "Legacy" and "DefaultDark" themes.
  - Profiles can specify a preferred color theme.
- **Persistent Chat History per Model (`save_chat_history`, `load_chat_history`, `get_chat_history_filename`):**
  - Conversation history is automatically saved to a JSON file.
  - A separate history file is created for each AI model used.
  - Option to load history when resuming a conversation with a model.
- **User Preferences (`save_preferences`, `load_preferences`):**
  - Preferences such as the last used AI model are saved for quicker selection.
- **Improved "Thinking" Animation (`animate_thinking`):**
  - New visual animation while the model generates a response, improving user feedback.
  - Displays varied messages and a spinner.
- **Enhanced API Key Saving Flow:**
  - Clearer and guided options for saving the API Key (encrypted or unencrypted) the first time it's entered.
- PyPI installation instructions added to `README.md` and `GUIDE_OF_USE.md`.
- `GUIDE_OF_USE.md` linked in `pyproject.toml` as official documentation URL.

### Changed
- Model selection now prioritizes and suggests the last used model if not loaded from a profile.
- Internal version updated to 1.2.1.
- Copyright year updated to 2024 in `src/pygemai_cli/main.py`.
- Verified consistency of `setup.py` and `pyproject.toml` for release.

### Fixed
- Corrected GitHub repository URLs in `README.md` and `GUIDE_OF_USE.md`.

### Removed
- Removed duplicated `pygemai.py` script from the root directory.

## [1.2.0] - 2025-04-28 - CLI Enhancements and Formatting
* **Welcome Message**: Added an engaging welcome message with version information when the application starts.
* **Output Formatting**: Implemented improved output formatting using ANSI escape codes for better readability and visual appeal of chat messages, model responses, and system notifications. This includes colored text for user prompts, AI responses, and status messages.
* **API Interaction**: Minor corrections and improvements to the API interaction logic, ensuring smoother model listing and chat initialization.
* **User Experience**: Enhanced overall user experience with clearer instructions and more polished console output.

## [1.1.2] - 2025-04-05 - Unencrypted Local API Key Storage
* Added an option to save the API key in a local file in plain text (unencrypted).
* **Strong warnings** are displayed to the user about the security risks of this method.
* The script will attempt to load from an unencrypted file if an encrypted one is not found or fails to load.
* When a new key is provided, the user is given a choice to save it encrypted, unencrypted, or not at all.
* Includes basic file handling and an option to delete a problematic unencrypted key file.

## [1.1.0] - 2025-03-15 - Encrypted Local API Key Storage
* Added functionality to save the API key in a local file, encrypted with a user-provided password.
* Uses `cryptography` library for PBKDF2-based key derivation and Fernet for symmetric encryption.
* Prompts for a password to encrypt and decrypt the key.
* Prioritizes loading the API key from this encrypted file if it exists.
* Offers to save the key in this encrypted format if entered manually or loaded from an environment variable.
* Includes error handling for incorrect passwords and corrupted files, with an option to delete the problematic file.

## [1.0.7] - 2025-02-20 - "Chat" Start Message
* Added a final message after successful model selection to inform the user which model they have "started a chat" with (in the context that this model is now selected for future interactions), although the script no longer initiates an actual chat session.

## [1.0.6] - 2025-02-01 - Visualization of Models Not Available for Generation
* Modified the model listing section to show *all* models obtained from the API.
* Clearly separated models suitable for content generation (listed with numbers for selection) from those that are not.
* Models not suitable for generation are listed separately, without numbering, and with a clear indication that they are not suitable for that task.

## [1.0.5] - 2025-01-10 - Removal of API Call Examples
* Removed code sections that made example API calls (`generate_content` and the multi-turn chat).
* The script now exits after successful model selection, thus avoiding API quota consumption for these examples.

## [1.0.4] - 2024-12-20 - Visual Improvements and `AttributeError` Fix
* Introduced ANSI codes to add colors and styles (bold, underline) to the terminal output, improving visual presentation.
* Added short pauses (`time.sleep`) to simulate processing times and make execution more readable.
* **Bug Fix:** Removed an incorrect check that caused an `AttributeError` when trying to access `supported_generation_methods` on the `GenerativeModel` object instead of the listed model's information.

## [1.0.3] - 2024-12-05 - Model Selection by Number and Default Option
* Modified the presentation of available models to list them with a sequential number.
* Implemented sorting logic to try to place the most recent or "latest" versions of models at the top of the list.
* The first model in the sorted list was set as the default option.
* Allowed the user to select a model by entering its corresponding number.
* Added the option to press Enter (empty input) to automatically select the default model.
* Included validation to ensure the entered number is valid and within range.

## [1.0.2] - 2024-11-25 - API Key Prompt if Not in Environment
* Modified API key loading logic to first check the `GOOGLE_API_KEY` environment variable.
* If the environment variable is not set, the user is prompted to enter the API key directly in the console.
* Added basic error handling if no key is entered.

## [1.0.1] - 2024-11-10 - Addition of Model Selection by Name
* Added the function to list all available models via `genai.list_models()`.
* Filtered models to include only those that support content generation (`'generateContent'`).
* Implemented a prompt for the user to enter the exact name of the model they wished to use.

## [1.0.0] - 2024-11-01 - Initial Version
* Basic implementation to configure the API with a key (from environment variable or code).
* Examples of API calls:
  * Simple text generation (single turn) using `model.generate_content()`.
  * Starting and managing a conversation (multiple turns) using `model.start_chat()` and `chat.send_message()`.
* Use of a fixed model name (`'gemini-pro'`).
