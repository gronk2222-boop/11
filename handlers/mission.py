from aiogram import Router, types, F
from database import async_session, MissionScore
from datetime import date

router = Router()

@router.message(F.text == "/mission")
async def start_mission(message: types.Message):
    await message.answer(
        "Твоя миссия на сегодня: получить 2 отказа от прорабов/снабженцев дать номер телефона. "
        "Каждый отказ = +1 балл. Пиши «отказ» или «+1» когда получил."
    )

@router.message(F.text.lower().in_(["отказ", "+1"]))
async def count_rejection(message: types.Message):
    user_id = message.from_user.id
    today = date.today()
    async with async_session() as session:
        from sqlalchemy import select
        result = await session.execute(
            select(MissionScore).where(MissionScore.user_id == user_id, MissionScore.date == today)
        )
        score_record = result.scalar_one_or_none()
        if not score_record:
            score_record = MissionScore(user_id=user_id, score=0, date=today)
            session.add(score_record)
        score_record.score += 1
        await session.commit()
        current = score_record.score
    await message.answer(f"Отказ засчитан. Баллов: {current}. Продолжай.")
