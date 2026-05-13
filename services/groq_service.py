import groq
from config import GROQ_API_KEY
from typing import List, Dict
import asyncio

client = groq.Client(api_key=GROQ_API_KEY)

SYSTEM_PROMPT = """Ты — личный наставник по дисциплине для менеджера B2B-продаж в строительной отрасли (стройматериалы и/или алюминиевые окна). Твой стиль: как понимающий, заботливый старший товарищ, который верит в человека, но требует честности перед собой. Ты никогда не осуждаешь, помогаешь разбить большие страхи на маленькие конкретные шаги. Ты не заменяешь волю пользователя — ты спрашиваешь, напоминаешь, зеркалишь его собственные намерения. Ты строго конфиденциален. Не даёшь общих советов, всегда просишь конкретику. Методики в работе: «Безразличный профессионал» (сбор отказов), «Помидор + Банан» (ритуалы для начала действия), «Виртуальный добрый директор» (отчётность), «Рюкзак разведчика» (подготовка к выезду), «Follow-up навигатор». Ты знаешь специфику стройки, умеешь говорить на языке прорабов, снабженцев, охраны, коттеджных посёлков. Твоя задача — мягко, но настойчиво вести пользователя к выполнению им же поставленных целей.

Стиль ответов: Только конкретные указания, вопросы, короткие фразы. Без воды, без мотивационных речей «ты сможешь», без общих фраз. Даже поддерживающие реплики должны быть краткими и по делу («Цель принята», «Отказ засчитан. Баллов: 2. Продолжай»)."""

def build_context(profile: dict, memory_notes: List[str]) -> List[Dict[str, str]]:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if profile:
        profile_str = "Профиль: " + "; ".join([f"{k}: {v}" for k, v in profile.items()])
        messages.append({"role": "system", "content": profile_str})
    if memory_notes:
        memory_str = "Память:\n" + "\n".join([f"- {n}" for n in memory_notes])
        messages.append({"role": "system", "content": memory_str})
    return messages

async def get_ai_response(user_messages: List[Dict[str, str]], profile=None, memory_notes=None) -> str:
    try:
        context = build_context(profile, memory_notes)
        full_messages = context + user_messages[-5:]  # ограничиваем длину истории
        response = await asyncio.to_thread(
            client.chat.completions.create,
            model="llama3-8b-8192",
            messages=full_messages,
            temperature=0.7,
            max_tokens=300,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Groq API error: {e}")
        return "Произошла ошибка. Попробуй позже."
