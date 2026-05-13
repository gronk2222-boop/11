import pytest
from unittest.mock import AsyncMock, patch
from database import async_session, UserProfile, DailyGoal
from encryption import encrypt

@pytest.mark.asyncio
async def test_forget_deletes_all():
    user_id = 999
    # Добавляем тестовые данные
    async with async_session() as session:
        session.add(UserProfile(user_id=user_id, encrypted_data=b"data"))
        session.add(DailyGoal(user_id=user_id, encrypted_goal=encrypt(user_id, "goal")))
        await session.commit()

    # Вызов команды /forget
    from handlers.forget import forget_data
    message = AsyncMock()
    message.from_user.id = user_id
    await forget_data(message)

    # Проверяем, что данные удалены
    async with async_session() as session:
        from sqlalchemy import select
        result = await session.execute(select(UserProfile).where(UserProfile.user_id == user_id))
        assert result.scalar_one_or_none() is None
        result = await session.execute(select(DailyGoal).where(DailyGoal.user_id == user_id))
        assert result.scalars().all() == []

    message.answer.assert_called_with("Все данные удалены.")
