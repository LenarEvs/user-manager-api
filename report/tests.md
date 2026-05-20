# Agent Test Report

Дата проверки: 2026-05-20 (повторный прогон после исправлений)

## Preconditions

- API server started: `python -m uvicorn app.main:app --host 127.0.0.1 --port 8001`
- API health check: `GET /health` -> `{"status":"ok"}`
- Agent run command: `python langchain-agent/main.py "<query>"`

## Test cases (5 user queries)

### 1) Query
`list all users via api`

Response:
```text
Status: success
Action: list all users via api
Data: []
Errors: -
```

### 2) Query
`create user via api with name Alex and email alex@example.com`

Response:
```text
Status: success
Action: create user via api with name Alex and email alex@example.com
Data: {"id": 1, "name": "Alex", "email": "alex@example.com"}
Errors: -
```

### 3) Query
`create user via api with name Kate and email kate@example.com`

Response:
```text
Status: success
Action: create user via api with name Kate and email kate@example.com
Data: {"id": 2, "name": "Kate", "email": "kate@example.com"}
Errors: -
```

### 4) Query
`get user by id 1 via api`

Response:
```text
Status: success
Action: get user by id 1 via api
Data: {"id": 1, "name": "Alex", "email": "alex@example.com"}
Errors: -
```

### 5) Query
`list all users via api`

Response:
```text
Status: success
Action: list all users via api
Data: [{"id": 1, "name": "Alex", "email": "alex@example.com"}, {"id": 2, "name": "Kate", "email": "kate@example.com"}]
Errors: -
```
