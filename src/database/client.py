import asyncio
from sqlalchemy.sql import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# postgresql+asyncpg://<username>:<password>@<host>:<port>/<database>
DATABASE_URL = "postgresql+asyncpg://postgres:admin@localhost:5432/fastapi"

# Crear motor asincrónico
engine = create_async_engine(DATABASE_URL, future=True, echo=True)

# Crear la sesión asincrónica
async_session = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

# Dependencia para obtener la sesión
async def get_db():
    async with async_session() as session:
        yield session

async def test_connection():
    engine = create_async_engine(DATABASE_URL, future=True, echo=True)
    async with engine.connect() as conn:
        result = await conn.execute(text("SELECT 1"))
        print(result.fetchone())

if __name__ == "__main__":
    asyncio.run(test_connection())
