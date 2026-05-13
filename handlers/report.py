from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import async_session, DailyGoal, UserProfile
from encryption import decrypt
from datetime import date

router = Router()

class ReportState(StatesGroup):
    waiting_for_completion = State()

@router.message(F.text == "/report")
async def report(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    today = date.today()
    async with async_session() as session:
        from sqlalchemy import select
        result = await session.execute(
            select(DailyGoal).where(DailyGoal.user_id == user_id, DailyGoal.date == today)
        )
        goal = result.scalar_one_or_none()
        if not goal:
            await message.answer("Сегодня цель не ставилась.")
            return
        decrypted_goal = decrypt(user_id, goal.encrypted_goal)
        await message.answer(f"Твоя цель на сегодня: {decrypted_goal}\nВыполнена? (да/нет)")
        await state.set_state(ReportState.waiting_for_completion)

@router.message(ReportState.waiting_for_completion, F.text.lower().in_(["да", "нет"]))
async def process_report(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    completed = message.text.lower() == "да"
    today = date.today()
    async with async_session() as session:
        from sqlalchemy import select
        result = await session.execute(
            select(DailyGoal).where(DailyGoal.user_id == user_id, DailyGoal.date == today)
        )
        goal = result.scalar_one_or_none()
        if goal:
            goal.completed = completed
            await session.commit()
    await state.clear()
    if completed:
        await message.answer("Цель выполнена. Отличная работа.")
    else:
        # Проверяем наличие доброго директора
        async with async_session() as session:
            result = await session.execute(select(UserProfile).where(UserProfile.user_id == user_id))
            profile = result.scalar_one_or_none()
            director_name = "Добрый директор"
            if profile:
                import json
                data = json.loads(decrypt(user_id, profile.encrypted_data))
                if data.get("q4") and "да" in data["q4"].lower():
                    director_name = data["q4"]
            await message.answer(
                f"Представь, что {director_name} спрашивает: почему 0 контактов? Как ответишь завтра? Давай поставим реалистичную цель на завтра."
            )
