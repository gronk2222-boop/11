from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import BigInteger, LargeBinary, DateTime, Integer, Boolean
from datetime import datetime
from config import DATABASE_URL

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class UserProfile(Base):
    __tablename__ = "user_profiles"
    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    encrypted_data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class DailyGoal(Base):
    __tablename__ = "daily_goals"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    encrypted_goal: Mapped[bytes] = mapped_column(LargeBinary)
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)

class MissionScore(Base):
    __tablename__ = "mission_scores"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    score: Mapped[int] = mapped_column(Integer, default=0)

class Client(Base):
    __tablename__ = "clients"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    encrypted_name: Mapped[bytes] = mapped_column(LargeBinary)
    encrypted_object: Mapped[bytes] = mapped_column(LargeBinary)
    encrypted_notes: Mapped[bytes] = mapped_column(LargeBinary, nullable=True)
    last_contact: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class Memory(Base):
    __tablename__ = "memories"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    encrypted_fact: Mapped[bytes] = mapped_column(LargeBinary)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
