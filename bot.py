import asyncio
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import BOT_TOKEN
from database import init_db, async_session, UserProfile
from handlers import onboarding, goal, mission, tomato, report, clients, memory, forget

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Регистрация роутеров
dp.include_router(onboarding.router)
dp.include_router(goal.router)
dp.include_router(mission.router)
dp.include_router(tomato.router)
dp.include_router(report.router)
dp.include_router(clients.router)
dp.include_router(memory.router)
dp.include_router(forget.router)

async def set_commands():
    commands = [
        BotCommand(command="/start", description="Онбординг"),
        BotCommand(command="/goal", description="Поставить цель на день"),
        BotCommand(command="/mission", description="Режим сбора отказов"),
        BotCommand(command="/report", description="Отчёт за день"),
        BotCommand(command="/clients", description="Управление клиентами"),
        BotCommand(command="/memory", description="Память"),
        BotCommand(command="/forget", description="Удалить все данные"),
    ]
    await bot.set_my_commands(commands)

async def send_morning_message():
    """Утренняя рассылка запроса цели."""
    async with async_session() as session:
        from sqlalchemy import select
        result = await session.execute(select(UserProfile.user_id))
        users = result.scalars().all()
        for uid in users:
            try:
                await bot.send_message(uid, "Доброе утро. Поставь цель на день: /goal")
            except Exception as e:
                print(f"Не могу отправить сообщение пользователю {uid}: {e}")

async def send_evening_reminder():
    """Вечернее напоминание об отчёте."""
    async with async_session() as session:
        from sqlalchemy import select
        result = await session.execute(select(UserProfile.user_id))
        users = result.scalars().all()
        for uid in users:
            try:
                await bot.send_message(uid, "Время отчитаться: /report")
            except Exception as e:
                print(f"Не могу отправить напоминание {uid}: {e}")

async def on_startup():
    await init_db()
    await set_commands()
    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(send_morning_message, "cron", hour=9, minute=0)
    scheduler.add_job(send_evening_reminder, "cron", hour=20, minute=0)
    scheduler.start()

async def main():
    dp.startup.register(on_startup)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
