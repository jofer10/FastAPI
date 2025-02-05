# Proyecto de API con FastAPI y SQLAlchemy

Este proyecto es una API desarrollada con FastAPI y SQLAlchemy. La API permite gestionar usuarios y productos, y proporciona endpoints para el inicio de sesión y otras operaciones relacionadas.

## Requisitos

- Python 3.8+
- FastAPI
- SQLAlchemy
- Uvicorn
- Pydantic
- jose
- asyncpg

## Instalación

1. Clona el repositorio:

    ```bash
    git clone https://github.com/tu_usuario/tu_repositorio.git
    cd tu_repositorio
    ```

2. Crea un entorno virtual y actívalo:

    ```bash
    python -m venv env
    source env/bin/activate  # En Windows usa `env\Scripts\activate`
    ```

3. Instala las dependencias:

    ```bash
    pip install -r requirements.txt
    ```

## Configuración

Asegúrate de configurar tu base de datos en el archivo de configuración correspondiente. Puedes usar variables de entorno para gestionar las credenciales de la base de datos.

## Ejecución

Para ejecutar la aplicación, usa el siguiente comando:

```bash
uvicorn main:app --reload