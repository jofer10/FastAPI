from fastapi.responses import JSONResponse
from fastapi import status
import re
import sqlalchemy.dialects.postgresql.asyncpg

def exception_db(db_err):
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

def excepciones_generales(e):
    return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message":"Error inesperado. Exception: "+str(e)}
        )