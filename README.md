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

## LangChain агент (Ollama)

Агент расположен в `langchain-agent` и использует локальный Ollama.

### Подготовка

1. Убедитесь, что Ollama запущен локально.
2. Скопируйте пример окружения:

```bash
copy .env.example .env
```

3. Установите зависимости агента:

```bash
pip install -r langchain-agent/requirements.txt
```

### Запуск агента

```bash
python langchain-agent/main.py
```

Пример запроса агенту: `Получи список пользователей через API`.

Запуск с CLI-аргументом:

```bash
python langchain-agent/main.py "создай пользователя с именем Alex и email alex@example.com"
```

Формат ответа агента:

```text
Status: success | error
Action: <описание действия>
Data: <результат API>
Errors: <если есть>
```