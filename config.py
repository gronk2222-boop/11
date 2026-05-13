import os

def get_env_var(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"Missing required environment variable: {name}")
    return value

# Внутренние имена констант остаются прежними, чтобы не ломать остальной код
BOT_TOKEN = get_env_var("TELEGRAM_TOKEN")           # Railway: TELEGRAM_TOKEN
DATABASE_URL = get_env_var("SUPABASE_URL")          # Railway: SUPABASE_URL
GROQ_API_KEY = get_env_var("GROQ_API_KEY")          # Railway: GROQ_API_KEY
SUPABASE_KEY = get_env_var("SUPABASE_KEY")
