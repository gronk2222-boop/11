from aiogram import Router, types, F
from database import async_session, Memory
from encryption import decrypt

router = Router()

@router.message(F.text == "/memory")
async def show_memory(message: types.Message):
    user_id = message.from_user.id
    async with async_session() as session:
        from sqlalchemy import select
        result = await session.execute(
            select(Memory).where(Memory.user_id == user_id).order_by(Memory.timestamp.desc()).limit(5)
        )
        memories = result.scalars().all()
        if not memories:
            await message.answer("Память пуста.")
            return
        lines = [decrypt(user_id, m.encrypted_fact) for m in memories]
        await message.answer("Последние записи:\n" + "\n".join(lines))
