from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import async_session, DailyGoal
from encryption import encrypt
from services.validators import validate_goal
from datetime import datetime

router = Router()

class GoalState(StatesGroup):
    waiting_for_goal = State()

@router.message(F.text == "/goal")
async def ask_goal(message: types.Message, state: FSMContext):
    await state.set_state(GoalState.waiting_for_goal)
    await message.answer(
        "Что ты должен сделать сегодня за ближайшие 24 часа, чтобы вечером сказать себе: «Сегодня я жил не зря»?\n"
        "(Конкретное действие, без денежных целей)"
    )

@router.message(GoalState.waiting_for_goal)
async def process_goal(message: types.Message, state: FSMContext):
    goal = message.text.strip()
    if not validate_goal(goal):
        await message.answer("Цель не должна содержать деньги (заработать, рубли). Напиши конкретное действие.")
        return
    encrypted_goal = encrypt(message.from_user.id, goal)
    async with async_session() as session:
        session.add(DailyGoal(user_id=message.from_user.id, encrypted_goal=encrypted_goal, date=datetime.now()))
        await session.commit()
    await state.clear()
    await message.answer("Цель принята.")
