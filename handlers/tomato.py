from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
import re

router = Router()

class TomatoSteps(StatesGroup):
    ready = State()
    on_way = State()

TRIGGERS = [r"не могу заставить себя поехать", r"лень", r"не хочу ехать", r"прокрастинация", r"нет сил ехать"]

@router.message(F.text.regex(re.compile("|".join(TRIGGERS), re.IGNORECASE)))
async def tomato_start(message: types.Message, state: FSMContext):
    await state.set_state(TomatoSteps.ready)
    await message.answer(
        "Возьми визитки, ключи от машины, буклеты. Как положил в сумку — съешь кусочек шоколада/банана (или глоток кофе). Напиши мне: ГОТОВ"
    )

@router.message(TomatoSteps.ready, F.text.upper() == "ГОТОВ")
async def tomato_on_way(message: types.Message, state: FSMContext):
    await state.set_state(TomatoSteps.on_way)
    await message.answer("Теперь просто выйди из дома/офиса. Когда сядешь в машину — ещё кусочек. Напиши: В ПУТИ")

@router.message(TomatoSteps.on_way, F.text.upper() == "В ПУТИ")
async def tomato_arrived(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Ты сделал это. Запиши результат: ДОБЫЛ КОНТАКТ / ОТКАЗ. Гордись собой.")
