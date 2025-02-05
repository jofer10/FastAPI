import logging
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from src.routers import users, login
from src.database.client import async_session

# Configuración del logging
logging.basicConfig(
    level=logging.INFO,  # Nivel de logs: DEBUG, INFO, WARNING, ERROR, CRITICAL
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("app.log"),  # Guarda los logs en un archivo
        # logging.StreamHandler()  # Muestra los logs en la consola
    ]
)

logger = logging.getLogger("main")

app = FastAPI()

class TransactionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Crear una sesión manualmente desde el async_session
        async with async_session() as db:
            request.state.db = db  # Propagar la sesión
            try:
                # Procesar la solicitud
                response = await call_next(request)
                # Confirmar la transacción si no hubo errores
                await db.commit()
                return response
            except Exception as e:
                # Revertir la transacción en caso de error
                await db.rollback()
                raise e
            finally:
                # Asegurar el cierre de la conexión
                await db.close()


# Agregar el middleware
app.add_middleware(TransactionMiddleware)

# Middleware de CORS
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:3000", "https://mi-front-end.com"],  # Orígenes permitidos
    allow_origins=["*"],
    allow_credentials=True,  # Permitir cookies y credenciales
    allow_methods=["*"],  # Métodos permitidos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Headers permitidos
)

# Middleware para capturar requests y responses
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.method} {request.url}")

    # Captura la respuesta original
    response = await call_next(request)

    # Lee el cuerpo de la respuesta (esto funciona para JSON u otros tipos de contenido)
    response_body = b""
    async for chunk in response.body_iterator:
        response_body += chunk

    # Log de la data que retorna
    try:
        # Intenta decodificar si es JSON para mayor claridad
        response_data = response_body.decode('utf-8')
        logger.info(f"Response status: {response.status_code}, Body: {response_data}")
    except Exception as e:
        logger.warning(f"Could not decode response body: {e}")
        logger.info(f"Response status: {response.status_code}")

    # Reemplazar el body agotado usando StreamingResponse
    new_response = StreamingResponse(iter([response_body]), status_code=response.status_code)
    for header, value in response.headers.items():
        new_response.headers[header] = value

    return new_response

# APIs
app.include_router(users.router)
app.include_router(login.router)

@app.get("/")
async def root():
    return {"message": "¡Hola FastAPI!"}
