# Guía para Publicar Nuevas Versiones de PyGemAi en PyPI

Esta guía describe los pasos para publicar una nueva versión de PyGemAi en el Python Package Index (PyPI).

## 1. Prerrequisitos

*   **Python y Pip:** Asegúrate de tener Python y Pip instalados.
*   **Cuenta en PyPI:** Necesitas una cuenta en [PyPI](https://pypi.org/) y/o en [TestPyPI](https://test.pypi.org/) si deseas probar primero.
*   **Herramientas de Empaquetado:** Instala las herramientas necesarias si aún no las tienes:
    ```bash
    pip install --upgrade build twine
    ```

## 2. Configuración de Credenciales de PyPI (`.pypirc`)

Para subir paquetes, `twine` necesita tus credenciales de PyPI. Puedes configurarlas en un archivo `~/.pypirc` (en tu directorio home).

**Importante:** Nunca subas este archivo a tu repositorio Git.

Crea o edita el archivo `~/.pypirc` con el siguiente formato:

```ini
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-YOUR_PYPI_API_TOKEN

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-YOUR_TESTPYPI_API_TOKEN
```

*   **Tokens API:** Es **altamente recomendado** usar [Tokens API de PyPI](https://pypi.org/help/#apitokens) en lugar de tu nombre de usuario y contraseña directamente.
    *   Reemplaza `pypi-YOUR_PYPI_API_TOKEN` con tu token real para PyPI.
    *   Reemplaza `pypi-YOUR_TESTPYPI_API_TOKEN` con tu token real para TestPyPI.
    *   El `username` debe ser `__token__` cuando usas un token API.

## 3. Pasos para Publicar una Nueva Versión

### 3.1. Asegurar que el Repositorio Esté Actualizado
Asegúrate de que todos los cambios de código estén commiteados y que tu rama local esté actualizada con la rama principal del repositorio.

```bash
git status
# git pull (si es necesario)
```

### 3.2. Actualizar el Número de Versión
Antes de publicar, debes incrementar el número de versión del paquete. Edita los siguientes archivos:

*   `setup.py`:
    ```python
    # version="1.2.0",  # Versión anterior
    version="1.2.1",  # Nueva versión
    ```
*   `pyproject.toml`:
    ```toml
    # version = "1.2.0" # Versión anterior
    version = "1.2.1" # Nueva versión
    ```
*   `docs/Changelog.md`:
    *   Asegúrate de que el changelog esté actualizado con una entrada para la nueva versión.

**Nota sobre versionado:** Sigue el versionado semántico (SemVer) si es posible (MAJOR.MINOR.PATCH).

### 3.3. Limpiar Directorios de Construcción Anteriores (Opcional pero Recomendado)
Para evitar problemas con artefactos de construcciones anteriores:
```bash
rm -rf dist/ build/ *.egg-info
```

### 3.4. Construir el Paquete
Usa el módulo `build` para crear los archivos de distribución (sdist y wheel):
```bash
python -m build
```
Esto creará un directorio `dist/` con los archivos `.tar.gz` (sdist) y `.whl` (wheel).

### 3.5. Verificar los Contenidos del Paquete (Opcional pero Recomendado)
Puedes inspeccionar el contenido del archivo `.tar.gz` para asegurarte de que todos los archivos necesarios están incluidos.
```bash
tar tzf dist/PyGemAi-1.2.1.tar.gz  # Reemplaza con el nombre de tu archivo
```
Verifica también el wheel si es necesario con `unzip -l dist/PyGemAi-1.2.1-py3-none-any.whl`.

### 3.6. Subir a TestPyPI (Recomendado)
Es una buena práctica subir primero a TestPyPI para verificar que todo funciona correctamente.
```bash
twine upload --repository testpypi dist/*
```
Luego, puedes intentar instalarlo desde TestPyPI en un entorno virtual limpio:
```bash
pip install --index-url https://test.pypi.org/simple/ --no-deps PyGemAi
```
Prueba la funcionalidad básica.

### 3.7. Subir a PyPI (Producción)
Una vez que estés seguro de que el paquete funciona correctamente desde TestPyPI, súbelo a PyPI real:
```bash
twine upload dist/*
```

## 4. Después de Publicar

*   **Crear un Tag en Git:** Es una buena práctica crear un tag en Git para la versión que acabas de publicar.
    ```bash
    git tag v1.2.1
    git push origin v1.2.1
    ```
*   **Anunciar el Release:** Considera anunciar el nuevo release en los canales apropiados (si los tienes).

## 5. Recomendaciones Adicionales

*   **Formateo de Código:** Para mantener un estilo de código consistente y limpio, considera usar herramientas como `Black` y `autopep8` antes de commitear cambios.
    ```bash
    pip install black autopep8
    black .
    autopep8 --in-place --recursive .
    ```
*   **Linting:** Usa `flake8` para identificar posibles errores o problemas de estilo.
    ```bash
    pip install flake8
    flake8 src/
    ```
    Configura `flake8` según las necesidades del proyecto (ej. en `setup.cfg` o `.flake8`).

Siguiendo esta guía, el proceso de publicación debería ser más estructurado y menos propenso a errores.
