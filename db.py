from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker



db_url = f"postgresql+asyncpg://postgres:mutebaby@localhost/mohandes"
engine = create_async_engine(db_url)
async_session = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_session():
    async with async_session() as session:
        yield session