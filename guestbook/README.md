# Гостевая книга на FastAPI и SQLAlchemy

JSON API гостевой книги с сохранением отзывов в SQLite через асинхронный ORM SQLAlchemy 2.0 и миграциями Alembic.

## Установка и запуск



macOS у тебя мак вроде 

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m alembic upgrade head
python -m uvicorn main:app --reload