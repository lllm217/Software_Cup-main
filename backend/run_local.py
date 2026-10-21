"""Local single-worker runner with SQLite and a persistent random JWT key."""
import os
from pathlib import Path
import secrets


def configure():
    root = Path(__file__).resolve().parent
    os.chdir(root)
    from dotenv import load_dotenv
    load_dotenv(root / '.env', override=False)
    runtime = root / '.runtime'
    runtime.mkdir(exist_ok=True)
    os.environ.setdefault('DATABASE_URL', f"sqlite+aiosqlite:///{(runtime / 'learning.db').as_posix()}")
    os.environ.setdefault('AUTH_ENABLED', 'true')
    if not os.environ.get('JWT_SECRET'):
        secret = runtime / 'jwt-secret'
        if not secret.exists():
            secret.write_text(secrets.token_urlsafe(48), encoding='utf-8')
        os.environ['JWT_SECRET'] = secret.read_text(encoding='utf-8').strip()


if __name__ == '__main__':
    configure()
    import uvicorn
    uvicorn.run('main:app', host='127.0.0.1', port=8000, workers=1)
