# Список задач на FastAPI и SQLAlchemy

Учебный проект для третьей пары «Python и Web». Создайте задачу, измените её состояние и отфильтруйте список через Swagger UI. Данные сохраняются в SQLite с помощью асинхронного ORM SQLAlchemy 2.0.

В этом примере разбираем типизацию параметров, схемы Pydantic 2, OpenAPI, зависимости `Depends`, `AsyncSession`, миграции Alembic и `async`/`await`. Получение одной задачи и удаление оставлены для самостоятельной работы.

## Как запустить

Нужен Python 3.11 или новее. Откройте терминал в папке `fastapi-template`, рядом с `main.py`.

**macOS и Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m alembic upgrade head
python -m uvicorn main:app --reload
```

**Windows (PowerShell)**

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m uvicorn main:app --reload
```

Откройте [Swagger UI](http://127.0.0.1:8000/docs). Схема API доступна по адресу [openapi.json](http://127.0.0.1:8000/openapi.json). OpenAPI описывает API, а Swagger UI показывает интерактивную страницу для отправки запросов.

Команда `alembic upgrade head` создаёт таблицу задач в `tasks.sqlite3` и записывает применённую ревизию в `alembic_version`. Повторный `upgrade head` сохраняет записи и применяет только новые миграции. Остановка сервера — `Ctrl+C`. При следующем запуске активируйте окружение, примените новые миграции и запустите `uvicorn`; на Windows используйте путь к интерпретатору из блока выше.

Настройки миграций и приложение используют один путь к базе, относительно папки проекта. Выполняйте команды из папки с `alembic.ini` и `main.py`.

В `main:app` слева указано имя Python-модуля, справа — объект приложения. `--reload` перезапускает сервер после изменения исходников. Если порт 8000 занят, добавьте `--port 8001` и откройте `/docs` на этом порту.

## Первые запросы в Swagger UI

1. Раскройте `POST /tasks`, нажмите **Try it out**, замените тело и нажмите **Execute**:

   ```json
   {"title": "Разобраться с SQLAlchemy"}
   ```

   Проверьте `201` и запомните `id` созданной задачи.

2. Выполните `GET /tasks`. Ответ — массив объектов с полями `id`, `title` и `done`. Новые записи находятся в начале списка.
3. В `PATCH /tasks/{task_id}` укажите полученный ID и отправьте:

   ```json
   {"done": true}
   ```

   Проверьте `200` и изменённый объект. Повторный PATCH с тем же телом оставляет `done=true`.

4. В `GET /tasks` задайте query-параметр `done=true`, затем `done=false`. Чтобы снова получить все задачи, уберите значение фильтра.
5. Отправьте пустое название или название длиннее 120 символов. Найдите в ответе `422` поле `detail`, а внутри — `loc` и `msg`.
6. В PATCH укажите неизвестный положительный ID: получите `404`. Нечисловой ID или `0` отклоняется проверкой параметров с `422`.
7. Перезапустите приложение и убедитесь, что задачи сохранились.

Откройте DevTools браузера, вкладку **Network / Сеть**, и отправьте POST из Swagger UI. В **Payload** найдите JSON с `title`, в **Headers** — `Content-Type: application/json` и статус `201`.

## Маршруты

| Запрос | Назначение | Успешный ответ |
| --- | --- | --- |
| `GET /tasks` | Все задачи | `200`, массив задач |
| `GET /tasks?done=true` | Выполненные задачи | `200`, массив задач |
| `GET /tasks?done=false` | Невыполненные задачи | `200`, массив задач |
| `POST /tasks` | Создание из JSON `{"title": "..."}` | `201`, созданная задача |
| `PATCH /tasks/{task_id}` | Установка состояния из JSON `{"done": true}` | `200`, обновлённая задача |

Схема создания задачи содержит одно ограничение длины:

```python
from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
```

Название должно содержать от 1 до 120 символов. Пробелы учитываются в длине и сохраняются. Дополнительные поля при создании Pydantic по умолчанию игнорирует: например, `done` задаёт отдельный PATCH. В `TaskUpdate` включён `extra="forbid"` и строгая проверка boolean: используйте JSON `true`/`false`, строка `"false"` и число `1` отклоняются.

Query-параметры приходят строками. FastAPI преобразует допустимые значения `done`, включая `true`, `false`, `1` и `0`, в Python `bool`. Неверное значение, например `done=maybe`, даёт `422`.

## Где смотреть код

| Файл | Что в нём |
| --- | --- |
| [main.py](main.py) | Приложение, lifespan, маршруты и ORM-запросы |
| [models.py](models.py) | SQLAlchemy-модель `Task` и описание таблицы |
| [schemas.py](schemas.py) | Pydantic-схемы создания, изменения и ответа |
| [db.py](db.py) | Зависимость `get_session()`, которая выдаёт сессию на запрос |
| [alembic.ini](alembic.ini) | Настройки Alembic и расположение миграций |
| [migrations/env.py](migrations/env.py) | Подключение к SQLite и `Base.metadata` для сравнения схемы |
| [migrations/versions/0001_create_task.py](migrations/versions/0001_create_task.py) | Начальная миграция с `upgrade()` и `downgrade()` |
| [tests/test_tasks.py](tests/test_tasks.py) | Тесты API, валидации, OpenAPI и сохранения после перезапуска |
| [tests/test_migrations.py](tests/test_migrations.py) | Соответствие моделей миграциям, повторное применение и откат |
| [LESSON.md](LESSON.md) | Сценарий демонстрации и вопросы для обсуждения |

## SQLAlchemy и Pydantic

| Класс | Ответственность |
| --- | --- |
| `models.Task` | Отображает объекты на таблицу `task` в SQLite |
| `schemas.TaskCreate` | Проверяет JSON для создания задачи |
| `schemas.TaskUpdate` | Проверяет JSON изменения состояния |
| `schemas.TaskResponse` | Описывает поля HTTP-ответа |

Pydantic-схема сама не создаёт таблицу и не сохраняет объект. В `TaskResponse` настройка `from_attributes=True` позволяет читать данные из атрибутов ORM-объекта, а `response_model` задаёт проверку и сериализацию ответа.

`Mapped[int]` и `mapped_column()` в ORM-модели связывают Python-атрибут со столбцом. `Base.metadata` содержит описание таблиц. Alembic сравнивает его с реальной схемой базы и помогает подготовить миграцию. Таблицы создаёт команда миграции перед запуском сервера.

## Миграции Alembic

Миграция — файл с изменениями структуры БД. `revision` обозначает её версию, `down_revision` указывает на предыдущую. `upgrade()` описывает переход вперёд, `downgrade()` — обратный переход. `head` означает последнюю ревизию в истории.

| Команда | Назначение |
| --- | --- |
| `python -m alembic upgrade head` | Применить миграции до последней ревизии |
| `python -m alembic current` | Показать ревизию базы |
| `python -m alembic history` | Показать цепочку миграций |
| `python -m alembic revision --autogenerate -m "add_task_priority"` | Подготовить файл по отличиям моделей от БД |
| `python -m alembic check` | Проверить, что autogenerate не находит новых операций |
| `python -m alembic downgrade -1` | Откатить последнюю применённую миграцию |

Окружение Alembic уже настроено, повторный `alembic init` для этого шаблона не нужен. В новом проекте с асинхронным драйвером начать можно с `python -m alembic init -t async migrations`.

`--autogenerate` создаёт файл-кандидат и не применяет его к базе. Прочитайте `upgrade()` и `downgrade()` перед `upgrade head`: например, переименование столбца инструмент может представить как удаление и создание. `create_all()` создаёт отсутствующие таблицы, но не переносит изменения в существующие. В этом шаблоне схему ведём через Alembic.

Откат выполняет код `downgrade()` выбранной ревизии. У начальной миграции `0001` это удаление всей таблицы задач. В демонстрации ниже откатываем второй шаг, который добавляет поле, и используем учебную копию базы.

### Демонстрация изменения модели

Используйте учебную копию проекта. Сначала примените начальную миграцию, запустите сервер и добавьте несколько задач. Затем остановите сервер и добавьте внутрь класса `Task` в `models.py`:

```python
priority: Mapped[int] = mapped_column(default=0, server_default="0")
```

В терминале выполните:

```bash
python -m alembic revision --autogenerate -m "add_task_priority"
```

Откройте новый файл в `migrations/versions/`: в `upgrade()` должно быть добавление столбца `priority` с `nullable=False` и значением по умолчанию `0` на стороне БД, в `downgrade()` — его удаление. Для SQLite генератор использует `batch_alter_table`, чтобы поддерживать изменения таблиц.

```bash
python -m alembic upgrade head
python -m alembic current
python -m alembic check
```

В Python shell из папки проекта проверьте данные:

```python
import sqlite3
from contextlib import closing

with closing(sqlite3.connect("tasks.sqlite3")) as connection:
    print(connection.execute("SELECT id, title, priority FROM task").fetchall())
```

Существующие задачи сохранятся и получат приоритет `0`. `default=0` задаёт значение для вставки через ORM, `server_default="0"` задаёт значение на стороне БД и позволяет добавить обязательный столбец к уже заполненной таблице. Поля HTTP-ответа задаёт `TaskResponse`: для вывода приоритета через API добавьте его и в схему ответа.

После изменения можно показать откат на той же учебной копии:

```bash
python -m alembic downgrade -1
python -m alembic current
python -m alembic upgrade head
```

В этой демонстрации откат удаляет столбец `priority` вместе с его значениями. Пока поле остаётся в ORM-модели, перед запуском сервера снова выполните `upgrade head`, чтобы модель и база соответствовали друг другу. Новый файл миграции сохраняйте вместе с исходниками.

### Если база осталась от версии с create_all

У прежней версии шаблона таблица могла быть создана без истории Alembic. Если `upgrade head` сообщает `table task already exists`, проверьте, что структура таблицы соответствует начальной миграции `0001_create_task.py`. Для неизменённой базы из предыдущего шаблона можно отметить уже существующую схему:

```bash
python -m alembic stamp 0001
python -m alembic check
```

`stamp` только записывает номер ревизии. Используйте его для базы, которая уже соответствует этой ревизии. Если схема отличается, сначала разберите расхождения; `stamp` не исправляет таблицы.

## Engine, Session и Depends

Dependency injection — обработчик объявляет, что ему нужно для работы, а фреймворк передаёт готовую зависимость. Здесь такой зависимостью служит сессия БД.

- `AsyncEngine` управляет подключениями и взаимодействием с драйвером. Его создаём при старте приложения и освобождаем при остановке.
- `async_sessionmaker` — фабрика сессий. `AsyncSession` отслеживает ORM-объекты и выполняет операции в транзакции.
- `Depends(get_session)` вызывает зависимость и передаёт отдельную сессию обработчику запроса. `yield` выдаёт сессию, выход из `async with` закрывает её. Незавершённая транзакция откатывается.

Зависимость указываем прямо в параметре обработчика:

```python
@app.get("/tasks", response_model=list[TaskResponse])
async def task_list(
    session: AsyncSession = Depends(get_session),
    done: bool | None = None,
):
    ...
```

`AsyncSession` задаёт тип параметра, `Depends(get_session)` сообщает FastAPI, как получить его значение.

Сессия SQLAlchemy относится к работе с базой данных. Сессию пользователя и cookie здесь не рассматриваем. Не передавайте одну `AsyncSession` одновременно нескольким независимым асинхронным задачам.

Создание записи в нашем обработчике:

```python
new_task = Task(title=task.title)
session.add(new_task)
await session.commit()
await session.refresh(new_task)
```

`add()` регистрирует объект в сессии. `commit()` отправляет накопленные изменения и фиксирует транзакцию, `refresh()` перечитывает поля объекта из базы. При изменении существующей задачи достаточно присвоить новое значение её атрибуту и вызвать `commit()`.

Выборка:

```python
statement = select(Task).where(Task.done.is_(False)).order_by(Task.id.desc())
result = await session.execute(statement)
tasks = result.scalars().all()
```

`select()` строит запрос, `execute()` выполняет его, `scalars()` извлекает ORM-объекты из строк результата. Здесь `all()` работает с уже полученным результатом и не требует `await`. В исходном обработчике условие использует значение фильтра `Task.done == done`.

## Где нужен await

Обработчики используют `async def`, потому что ждут асинхронные операции с БД. `commit()`, `refresh()`, `execute()` и `get()` у `AsyncSession` вызываются с `await`. У `session.add()` и построения `select()` ожидания нет.

Само `async def` не делает синхронный ввод-вывод асинхронным. SQLAlchemy использует URL `sqlite+aiosqlite`: `aiosqlite` предоставляет асинхронный интерфейс к SQLite, выполняя операции соединения в рабочем потоке. Это позволяет event loop обслуживать другие задачи во время ожидания, но не превращает SQLite в базу с неограниченным числом одновременных записей.

## Тесты

Из папки с `main.py`, в том же окружении:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -v
```

В PowerShell используйте `.\.venv\Scripts\python.exe` вместо `python`.

`TestClient` вызывает приложение без запуска Uvicorn. Фикстура `database_path` из `tests/conftest.py` применяет Alembic-миграции к отдельному файлу из `tmp_path`. Контекст `with TestClient(...)` запускает и завершает lifespan приложения. Рабочая база не используется. Сами тесты могут быть обычными `def`, хотя обработчики асинхронные.

## Самостоятельная работа

1. Добавьте `GET /tasks/{task_id}` с `response_model=TaskResponse`. Верните нужную задачу или `404`, если её нет.
2. Добавьте `DELETE /tasks/{task_id}`. При успешном удалении верните `204` с пустым телом. Неизвестный ID и повторное удаление должны давать `404`.
3. Проверьте новые операции через Swagger UI и добавьте pytest-тесты получения, отсутствия и удаления задачи. После удаления запись должна исчезнуть и из списка.

Подсказки: `await session.get(Task, task_id)`, `HTTPException`, `await session.delete(task)`, `await session.commit()` и `Response(status_code=204)`. Получайте сессию через `session: AsyncSession = Depends(get_session)` и используйте тип ID `TaskId` из `main.py`.

Дополнительно — параметр `limit` со значением от 1 до 100. Ограничьте число результатов через `.limit(limit)` и проверьте границы допустимых значений.

## Домашнее задание. Гостевая книга

Сделайте самостоятельный JSON API на FastAPI и SQLAlchemy.

- Опишите ORM-модель `Review` с ID, автором и текстом отзыва.
- Подготовьте миграцию Alembic для таблицы отзывов и включите её в исходники. В README укажите команду `upgrade head` перед запуском приложения.
- Создайте Pydantic-схемы входных данных и ответа. Сделайте поля обязательными, задайте ограничения длины через `Field`.
- Реализуйте создание отзыва (`POST /reviews`, `201`) и список отзывов (`GET /reviews`, `200`).
- Сохраняйте отзывы в SQLite через `AsyncSession`. Проверьте сохранение после перезапуска.
- Проверьте работу через Swagger UI. Добавьте тесты успешного создания и неверного ввода.
- Подготовьте README с командами установки, запуска и тестирования.

Дополнительно — очистка пробелов по краям и отклонение строк из одних пробелов, фильтрация по имени автора, получение одного отзыва и удаление с корректными `404` и `204`.

## Материалы

- [Первое приложение FastAPI и Swagger UI](https://fastapi.tiangolo.com/tutorial/first-steps/)
- [Зависимости с yield](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/)
- [Pydantic и поля](https://docs.pydantic.dev/latest/concepts/fields/)
- [SQLAlchemy 2.0 ORM](https://docs.sqlalchemy.org/en/20/orm/quickstart.html)
- [Асинхронный SQLAlchemy](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Учебник Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html)
- [Автогенерация миграций](https://alembic.sqlalchemy.org/en/latest/autogenerate.html)
- [Тестирование FastAPI](https://fastapi.tiangolo.com/tutorial/testing/)
