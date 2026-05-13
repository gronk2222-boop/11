from aiogram import Router, types, F
from database import async_session, UserProfile, DailyGoal, MissionScore, Client, Memory

router = Router()

@router.message(F.text == "/forget")
async def forget_data(message: types.Message):
    user_id = message.from_user.id
    async with async_session() as session:
        for model in [UserProfile, DailyGoal, MissionScore, Client, Memory]:
            from sqlalchemy import delete
            await session.execute(delete(model).where(model.user_id == user_id))
        await session.commit()
    await message.answer("Все данные удалены.")
