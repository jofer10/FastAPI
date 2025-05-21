from src.utils.logger import get_logger
import ast
from datetime import datetime, timedelta
import json
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import DBAPIError
from passlib.context import CryptContext
from jose import JWTError, jwt
from src.utils.exception_handler import exception_db, excepciones_generales
from src.models.response import LoginForm, LoginR

# Importar el logger configurado
logger = get_logger("main")

ALGORITHM = "HS256"
ACCESS_TOKEN_DURATION = 24
SECRET = "5513075f1700db977694aaf62bf55e1b3bd20eb23b5578ed17b3796cf214cb42"

router = APIRouter( prefix="/login", 
                    tags=["Login"],
                    responses={404: {
                        "description": "Not Found",
                        "content": {
                            "application/json": {
                                "example": {"message": "No encontrado."}
                            }
                        }
                    }}
                )

oauth2 = HTTPBearer()

crypt = CryptContext(schemes=["bcrypt"], bcrypt__rounds=10)

active_tokens = {}

def validate_jwt(credentials: HTTPAuthorizationCredentials = Depends(oauth2)):
    print("Credenciales: ",credentials)

    token = credentials.credentials

    print("Token recibido: "+token)

    try:
        usu_id = jwt.decode(token, SECRET, algorithms=ALGORITHM).get("sub")

        # El contenido de sub es de tipo str a pesar de que se guardó el objeto
        print("Usuario: ",ast.literal_eval(usu_id))

        if usu_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales de autenticación inválidas.",
                headers={"WWW-Authenticate": "Bearer"}
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="El token ha expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError as e:
        print(f"Error en la decodificación del token: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Error en la decodificación del token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("", response_model=LoginR)
async def login(form: LoginForm, request: Request):
    # Definimos la conexion con la bd
    db: AsyncSession = request.state.db

    # email = form.get("email")
    # password = form["password"]

    email = form.email
    password = form.password

    # Log de la solicitud de login
    logger.info(f"Login payload: {form.json()}")


    print(str(email)+' - '+str(password))

    # if "email" not in form or "password" not in form:
    #     return JSONResponse(
    #         status_code=400,
    #         content={"error": "JSON inválido."}
    #     )

    if email is None or password is None:
        return JSONResponse(
            status_code=400,
            content={"error": "JSON inválido."}
        )
    
    try:
        query = text("SELECT * FROM ufn_login_validacion_correo(:1)")
        params = {"1":email}

        result = await db.execute(query, params)
        user = result.fetchone()

        print(user)

        # Obtenemos la clave de base para la verificación
        pass_encryp = user.usu_key_access
        
        print(crypt.verify(password,pass_encryp))

        # Validamos
        if crypt.verify(password,pass_encryp):
            if user.usu_id in active_tokens:
                token_data = active_tokens[user.usu_id]
                try:
                    # Decode token to ensure it's still valid
                    jwt.decode(token_data["access_token"], SECRET, algorithms=[ALGORITHM])

                    return JSONResponse(
                    content={
                                "usuario": dict(user._mapping),
                                "refresh_token": token_data["access_token"],
                                "token_type":"bearer"
                            }
                )
                except jwt.ExpiredSignatureError:
                    pass
            
            print("TimeDelta: "+str(timedelta(hours=ACCESS_TOKEN_DURATION)))
            print("Fecha actual: "+str(datetime.now()))

            expire = datetime.now()+timedelta(hours=ACCESS_TOKEN_DURATION)

            print("Expira: "+str(expire))

            access_token = {"sub":json.dumps(dict(user._mapping)),"exp":expire.timestamp()}
            
            token = jwt.encode(access_token, SECRET, algorithm=ALGORITHM)
            active_tokens[user.usu_id]={"email":email,"access_token":token}
            print(json.dumps(active_tokens, indent=2))

            return JSONResponse(
                content={
                    "usuario": dict(user._mapping),
                    "access_token": token,
                    "token_type": "bearer"
                }
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message":"Correo y/o Contraseña incorrectos."}
            )
    except DBAPIError as db_err:
        return exception_db(db_err)
    except Exception as e:
        print("Error al ejecutar la consulta:", str(e))
        return excepciones_generales(e)

@router.get("/secure-endpoint")
def secure_endpoint(validate: None = Depends(validate_jwt)):
    return {"message": "Access granted"}