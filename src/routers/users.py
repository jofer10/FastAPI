import re
from typing import Dict
from passlib.context import CryptContext
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import JSONResponse
import sqlalchemy
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from sqlalchemy.exc import DBAPIError
from src.database.client import get_db
from src.models.user import Usuario
from src.models.response import UsuarioR
from src.utils.exception_handler import exception_db

router = APIRouter(prefix="/users", 
                    tags=["Users"],
                    responses={status.HTTP_404_NOT_FOUND: {
                        "description": "Not Found",
                        "content": {
                            "application/json": {
                                "example": {"message": "No encontrado."}
                            }
                        }
                    }}
                )

crypt = CryptContext(schemes=["bcrypt"], bcrypt__rounds=10)

@router.get("", response_model=list[UsuarioR])
async def getAllUsers(db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(text("SELECT * FROM sis_users_list(0)"))
        users = result.fetchall()
        
        # print([dict(row._mapping) for row in users])
        print(users)

        return users
    except DBAPIError as db_err:
        return exception_db(db_err)

@router.get("/{id}", response_model=Usuario)
async def getAllUsers(id: int, request: Request):
    print(id)
    db: AsyncSession = request.state.db
    
    try:
        query = text("SELECT * FROM sis_users_list(:1)")
        params = {"1":id}

        print("Parámetros:", params)
        print("Tipo de parámetros:", type(params))
        result = await db.execute(query, params)
        # await db.commit() # Asegura que se confirmen los cambios en la base de datos
        usuario = result.fetchone()
        print(usuario)

        return usuario
    except DBAPIError as db_err:  # Manejar errores relacionados con SQLAlchemy y DBAPI
        print("Error de la base de datos:", str(db_err.orig))  # La excepción original
        
        return exception_db(db_err)
    except Exception as e:
        print("Error al ejecutar la consulta:", str(e))
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message":"Error al crear el usuario."}
        )

@router.post("", response_model=Dict[str, str])
async def createUser(u: Usuario, request: Request):
    print(u)
    db: AsyncSession = request.state.db
    try:
        query = text("SELECT * FROM sis_users_ins_upd(:1, :2, :3, :4)")
        params = {"1":u.usu_id, "2":u.user, "3":u.email, "4":crypt.hash(u.password)}

        print("Parámetros:", params)
        print("Tipo de parámetros:", type(params))
        result = await db.execute(query, params)
        # await db.commit() # Asegura que se confirmen los cambios en la base de datos
        mensaje = result.fetchone()
        print(mensaje)

        return {"message": mensaje[0]} if mensaje else {"message": "No se encontró respuesta"}
    except DBAPIError as db_err:  # Manejar errores relacionados con SQLAlchemy y DBAPI
        print("Error de la base de datos:", str(db_err.orig))  # La excepción original
        match = re.search(r"ERROR:.*", str(db_err.orig))
        print(match)
        error_message = match.group(0) if match else "Error desconocido"
        print("Error exacto: "+error_message)

        if isinstance(db_err.orig, sqlalchemy.dialects.postgresql.asyncpg.AsyncAdapt_asyncpg_dbapi.Error):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": error_message},
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": "Error al procesar la consulta."},
            )
    except Exception as e:
        print("Error al ejecutar la consulta:", str(e))
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message":"Error al crear el usuario."}
        )

@router.put("", response_model=Dict[str, str])
async def updateUser(u: Usuario, request: Request):
    print(u)
    db: AsyncSession = request.state.db
    try:
        query = text("SELECT * FROM sis_users_ins_upd(:1, :2, :3, :4)")
        params = {"1":u.usu_id, "2":u.user, "3":u.email, "4":crypt.hash(u.password)}

        print("Parámetros:", params)
        print("Tipo de parámetros:", type(params))
        result = await db.execute(query, params)
        # await db.commit() # Asegura que se confirmen los cambios en la base de datos
        mensaje = result.fetchone()
        print(mensaje)

        return {"message": mensaje[0]} if mensaje else {"message": "No se encontró respuesta"}
    except DBAPIError as db_err:  # Manejar errores relacionados con SQLAlchemy y DBAPI
        print("Error de la base de datos:", str(db_err.orig))  # La excepción original
        match = re.search(r"ERROR:.*", str(db_err.orig))
        print(match)
        error_message = match.group(0) if match else "Error desconocido"
        print("Error exacto: "+error_message)

        if isinstance(db_err.orig, sqlalchemy.dialects.postgresql.asyncpg.AsyncAdapt_asyncpg_dbapi.Error):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": error_message},
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": "Error al procesar la consulta."},
            )
    except Exception as e:
        print("Error al ejecutar la consulta:", str(e))
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message":"Error al crear el usuario."}
        )

@router.delete("/{id}", response_model=Dict[str, str])
async def deleteUser(id: int, request: Request):
    db: AsyncSession = request.state.db
    try:
        query = text("SELECT * FROM sis_users_del(:1)")
        params = {"1":id}

        print("Parámetros:", params)
        print("Tipo de parámetros:", type(params))
        result = await db.execute(query, params)
        # await db.commit() # Asegura que se confirmen los cambios en la base de datos
        mensaje = result.fetchone()
        print(mensaje)

        return {"message": mensaje[0]} if mensaje else {"message": "No se encontró respuesta"}
    except DBAPIError as db_err:  # Manejar errores relacionados con SQLAlchemy y DBAPI
        print("Error de la base de datos:", str(db_err.orig))  # La excepción original
        match = re.search(r"ERROR:.*", str(db_err.orig))
        print(match)
        
        error_message = match.group(0) if match else "Error desconocido"
        print("Error exacto: "+error_message)

        if isinstance(db_err.orig, sqlalchemy.dialects.postgresql.asyncpg.AsyncAdapt_asyncpg_dbapi.Error):
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": error_message},
            )
        else:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"message": "Error al procesar la consulta."},
            )
    except Exception as e:
        print("Error al ejecutar la consulta:", str(e))
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message":"Error al crear el usuario."}
        )