from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from database import async_session, Client
from encryption import encrypt, decrypt
from datetime import datetime, timedelta

router = Router()

class ClientForm(StatesGroup):
    waiting_for_name = State()
    waiting_for_object = State()
    waiting_for_notes = State()

@router.message(F.text == "/clients")
async def clients_menu(message: types.Message):
    await message.answer("/addclient — добавить, /listclients — список, /checkfollowup — напоминания")

@router.message(F.text == "/addclient")
async def add_client_start(message: types.Message, state: FSMContext):
    await state.set_state(ClientForm.waiting_for_name)
    await message.answer("Имя клиента/прораба:")

@router.message(ClientForm.waiting_for_name)
async def client_name(message: types.Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(ClientForm.waiting_for_object)
    await message.answer("Объект/компания:")

@router.message(ClientForm.waiting_for_object)
async def client_object(message: types.Message, state: FSMContext):
    await state.update_data(object=message.text)
    await state.set_state(ClientForm.waiting_for_notes)
    await message.answer("Примечание (дата последнего контакта, контекст):")

@router.message(ClientForm.waiting_for_notes)
async def client_notes(message: types.Message, state: FSMContext):
    data = await state.get_data()
    user_id = message.from_user.id
    enc_name = encrypt(user_id, data["name"])
    enc_object = encrypt(user_id, data["object"])
    enc_notes = encrypt(user_id, message.text)
    async with async_session() as session:
        session.add(Client(user_id=user_id, encrypted_name=enc_name, encrypted_object=enc_object,
                          encrypted_notes=enc_notes, last_contact=datetime.now()))
        await session.commit()
    await state.clear()
    await message.answer("Клиент добавлен.")

@router.message(F.text == "/listclients")
async def list_clients(message: types.Message):
    user_id = message.from_user.id
    async with async_session() as session:
        from sqlalchemy import select
        result = await session.execute(select(Client).where(Client.user_id == user_id))
        clients = result.scalars().all()
        if not clients:
            await message.answer("Клиентов нет.")
            return
        lines = []
        for c in clients:
            name = decrypt(user_id, c.encrypted_name)
            obj = decrypt(user_id, c.encrypted_object)
            lines.append(f"{name} – {obj}")
        await message.answer("Твои клиенты:\n" + "\n".join(lines))

@router.message(F.text == "/checkfollowup")
async def check_followup(message: types.Message):
    user_id = message.from_user.id
    now = datetime.now()
    threshold = now - timedelta(days=10)
    async with async_session() as session:
        from sqlalchemy import select
        result = await session.execute(
            select(Client).where(Client.user_id == user_id, Client.last_contact < threshold)
        )
        stale_clients = result.scalars().all()
        if not stale_clients:
            await message.answer("Все контакты свежие.")
            return
        mentions = []
        for c in stale_clients:
            name = decrypt(user_id, c.encrypted_name)
            obj = decrypt(user_id, c.encrypted_object)
            mentions.append(f"{name} ({obj})")
        await message.answer(
            "Давно не было контакта:\n" + "\n".join(mentions) +
            "\nПредлагаю написать или позвонить."
        )
