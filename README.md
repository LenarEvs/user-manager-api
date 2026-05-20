# User Manager API

Минимальный API-проект для управления пользователями.

## Установка

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Запуск

```bash
uvicorn app.main:app --reload
```

## Эндпоинты

- `GET /health` - проверка доступности API
- `POST /users` - создать пользователя
- `GET /users` - получить список пользователей
- `GET /users/{user_id}` - получить пользователя по ID
- `PATCH /users/{user_id}` - обновить пользователя
- `DELETE /users/{user_id}` - удалить пользователя
# user-manager-api