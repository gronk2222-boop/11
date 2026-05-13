from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import async_session, UserProfile
from encryption import encrypt
import json

router = Router()

QUESTIONS = [
    "Что самое сложное в работе прямо сейчас (звонки, выезды, возражения, поиск контактов)?",
    "Чего боишься больше: звонить, ездить на объекты, не закрыть сделку, выглядеть глупо перед прорабом?",
    "Есть ли ощущение «могу больше, но что-то держит»?",
    "Есть ли у тебя «добрый директор» или человек, которому можно передать холодный прозвон?",
    "В какой именно нише ты работаешь (стройматериалы, окна, другое)?",
]

class Onboarding(StatesGroup):
    waiting_for_answer = State()

@router.message(F.text == "/start")
async def start_onboarding(message: types.Message, state: FSMContext):
    # Проверяем существование профиля
    async with async_session() as session:
        from sqlalchemy import select
        result = await session.execute(select(UserProfile).where(UserProfile.user_id == message.from_user.id))
        if result.scalar_one_or_none():
            await message.answer("Ты уже прошёл онбординг. Чем помочь?")
            return
    await state.set_state(Onboarding.waiting_for_answer)
    await state.update_data(answers=[], question_index=0)
    await message.answer(
        "Привет. Я — твой личный тренер по продажам в стройке.\n"
        "Всё, что ты мне расскажешь о страхах, лени или клиентах, останется строго между нами. "
        "Ни директор, ни коллеги никогда не увидят наших диалогов.\n"
        "Ты можешь материться, бояться, жаловаться — я пойму и не осужу."
    )
    await message.answer(QUESTIONS[0])

@router.message(Onboarding.waiting_for_answer)
async def process_answer(message: types.Message, state: FSMContext):
    data = await state.get_data()
    answers = data.get("answers", [])
    index = data.get("question_index", 0)
    answers.append(message.text)
    index += 1
    if index < len(QUESTIONS):
        await state.update_data(answers=answers, question_index=index)
        await message.answer(QUESTIONS[index])
    else:
        profile_dict = {f"q{i+1}": ans for i, ans in enumerate(answers)}
        encrypted = encrypt(message.from_user.id, json.dumps(profile_dict, ensure_ascii=False))
        async with async_session() as session:
            session.add(UserProfile(user_id=message.from_user.id, encrypted_data=encrypted))
            await session.commit()
        await state.clear()
        await message.answer("Профиль сохранён. Теперь ты можешь ставить цель: /goal")
