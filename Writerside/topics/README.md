# Gemini API Model Selection Script

This Python script allows you to list the available Gemini models via the API, select one for future use, and configure your API key.

## Description

The script performs the following tasks:

1.  Configures the Google Generative AI library using your API key.
2.  Attempts to load the API key from an environment variable (`GOOGLE_API_KEY`).
3.  If the environment variable is not set, it prompts you to enter the key directly in the console, providing instructions on how to set the environment variable for more secure usage.
4.  Lists all Gemini models available through your API key.
5.  Categorizes models based on their primary capabilities (Content Generation, Embedding, Other).
6.  Presents models suitable for Content Generation with a number for easy selection.
7.  Sorts Content Generation models to attempt to show the most recent or "latest" version first, setting the first one as the default option.
8.  Allows you to select a model by entering its number or pressing Enter to use the default.
9.  Displays a warning about potential variability in actual model availability.
10. Finishes after the selection, indicating which model was chosen.

## Prerequisites

* Python 3.7 or higher installed. You can download it from [python.org](https://www.python.org/).
* A Google Gemini API key. You can obtain one from [Google AI Studio](https://aistudio.google.com/).

## Installation

Follow these steps to set up your environment and install dependencies:

1.  **Clone or download** this Python script (`PyGemAi.py`).
2.  Open your **terminal or command prompt**.
3.  Navega hasta el **directorio** donde guardaste el script.
    ```bash
    cd /path/to/your/script
    ```
4.  **(Optional but recommended)** **Create a virtual environment** to isolate project dependencies:
    ```bash
    python -m venv venv
    ```
    This will create a directory named `venv` in your current directory.
5.  **Activate the virtual environment**:
    * **On Windows:**
        ```cmd
        venv\Scripts\activate
        ```
    * **On macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```
    You'll see the virtual environment name (e.g., `(venv)`) at the start of your command prompt, indicating it's active.
6.  Ensure your virtual environment is active, then **install the Google Generative AI library** by running:
    ```bash
    pip install google-generativeai
    ```
    This will install the library within your virtual environment.
7.  **(Optional) Verify installation**: You can try importing the library in an interactive Python session within the activated environment:
    ```bash
    python
    >>> import google.generativeai
    >>> # If no errors, installation was successful.
    >>> exit()
    ```

## API Key Configuration

It is **highly recommended** to configure your API key as an environment variable to avoid exposing it directly in your source code.

* **Linux/macOS:**
    ```bash
    export GOOGLE_API_KEY='YOUR_API_KEY'
    ```
* **Windows (CMD):**
    ```cmd
    set GOOGLE_API_KEY='YOUR_API_KEY'
    ```
* **Windows (PowerShell):**
    ```powershell
    $env:GOOGLE_API_KEY='YOUR_API_KEY'
    ```

Replace `'YOUR_API_KEY'` with your actual key. You must run the script in the same terminal session where you set the environment variable.

If you do not configure the environment variable, the script will prompt you to enter the key manually when run (less secure for production).

## Usage

1.  Open your terminal or command prompt.
2.  Navega hasta el directorio donde guardaste el script (`PyGemAi.py`).
3.  **Activate your virtual environment** if you created one (see step 5 in Installation).
4.  Execute the script:
    ```bash
    python PyGemAi.py
    ```
    (The script file name is `PyGemAi.py`).

5.  The script will list the available models, categorized by their primary function.
6.  You will be prompted to enter the number of the Content Generation model you wish to select.
7.  Press Enter without entering a number to select the default model (the first one in the numbered list).
8.  The script will confirm the selected model and finish.

## Changelog

```markdown
# Changelog - Gemini API Call Script
#
# This document details the modifications made to the Python script for interacting with the Gemini API.
#
# ## Initial Version
#
# * Basic implementation to configure the API with a key (from variable de entorno or code).
# * Examples of API calls:
#     * Simple text generation (single turn) using `model.generate_content()`.
#     * Starting and handling a conversation (multi-turn) using `model.start_chat()` and `chat.send_message()`.
# * Usage of a fixed model name (`'gemini-pro'`).
#
# ## Added Model Selection by Name
#
# * Added the functionality to list all available models via `genai.list_models()`.
# * Filtered models to include only those supporting content generation (`'generateContent'`).
# * Implemented a prompt for the user to enter the exact name of the desired model.
#
# ## API Key Prompt if Not in Environment
#
# * Modified the API key loading logic to first check the `GOOGLE_API_KEY` environment variable.
# * If the environment variable is not set, prompts the user to enter the API key directly in the console.
# * Added basic error handling if no key is entered.
#
# ## Model Selection by Number and Default Option
#
# * Changed the presentation of available models to list them with a sequential number.
# * Implemented sorting logic to attempt to place the most recent or "latest` of the models at the beginning of the list.
# * The first model in the sorted list was set as the default option.
# * Allowed the user to select a model by entering its corresponding number.
# * Added the option to press Enter (empty input) to automatically select the default model.
# * Included validation to ensure the entered number is valid and within range.
#
# ## Visual Improvements and Error Correction (`AttributeError`)
#
# * Introduced ANSI codes to add colors and styles (bold, underline) to the terminal output, improving visual presentation.
# * Added short pauses (`time.sleep`) to simulate processing times and make execution more readable.
# * **Bug Fix:** Removed an incorrect check that caused an `AttributeError` by attempting to access `supported_generation_methods` on the `GenerativeModel` object instead of the listed model information.
#
# ## Removed API Call Examples
#
# * Removed the code sections that performed example API calls (`generate_content` and the multi-turn chat).
# * The script now finishes after successful model selection, thus avoiding API quota consumption for these examples.
#
# ## Displayed Models Not Available for Generation
#
# * Modified the model listing section to show *all* models obtained from the API.
# * Clearly separated models suitable for content generation (listados with numbers for selection) from those that are not.
# * Models not suitable for generation are listed separately, without numbers, and with a clear indication that they are not appropriate for that task.
#
# ## "Chat" Start Message
#
# * Added a final message after successful model selection to inform the user which model they have "started a chat" with (in the context that this model is now selected for future interactions), even though the script no longer initiates a real chat session.
#
# This changelog summarizes the script's evolution through different iterations.