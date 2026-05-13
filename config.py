import os

def get_env_var(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"Missing required environment variable: {name}")
    return value

BOT_TOKEN = get_env_var("BOT_TOKEN")
DATABASE_URL = get_env_var("DATABASE_URL")
GROQ_API_KEY = get_env_var("GROQ_API_KEY")
ENCRYPTION_SALT = get_env_var("ENCRYPTION_SALT").encode()
