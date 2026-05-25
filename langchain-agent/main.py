import os
import sys
import json
import urllib.error
import urllib.request
from typing import Any

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.tools import tool
from langchain_core.messages import ToolMessage
from langchain_ollama import ChatOllama

load_dotenv()

SYSTEM_PROMPT = """
Роль: ты API-оператор для user-manager API.

Ограничения:
- Работай только с данными пользователей через доступные tools.
- Не выдумывай результаты API и не утверждай успех операции без вызова tool.
- Не выполняй действия вне контекста пользователей.

Правила вызова tools:
- Для чтения списка пользователей используй fetch_users_from_api без user_id.
- Для чтения конкретного пользователя используй fetch_users_from_api с user_id.
- Для создания пользователя используй create_user_via_api.
- Сначала вызывай tool, потом формируй краткий ответ на основе его JSON-результата.

Формат ответа всегда фиксированный:
Status: success | error
Action: <описание действия>
Data: <результат API>
Errors: <если есть>
""".strip()


def call_user_api(path: str, method: str = "GET", payload: dict[str, Any] | None = None) -> dict[str, Any]:
    base_url = os.getenv("USER_API_BASE_URL", "http://localhost:8001")
    url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"
    headers = {"Content-Type": "application/json"}
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(url=url, data=body, headers=headers, method=method)
    print(f"[tool] call_user_api -> method={method} url={url} payload={payload}")

    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            raw_body = response.read().decode("utf-8")
            parsed_body: Any
            if raw_body:
                try:
                    parsed_body = json.loads(raw_body)
                except json.JSONDecodeError:
                    parsed_body = raw_body
            else:
                parsed_body = None

            return {
                "ok": True,
                "status_code": response.status,
                "url": url,
                "data": parsed_body,
            }
    except urllib.error.HTTPError as exc:
        error_body = exc.read().decode("utf-8", errors="replace")
        return {
            "ok": False,
            "status_code": exc.code,
            "url": url,
            "error": error_body or exc.reason,
        }
    except urllib.error.URLError as exc:
        return {
            "ok": False,
            "status_code": None,
            "url": url,
            "error": str(exc.reason),
        }
    finally:
        print(f"[tool] call_user_api <- method={method} url={url}")


@tool
def fetch_users_from_api(user_id: str = "") -> str:
    """Вызывает HTTP API пользователей и возвращает JSON-ответ как строку."""
    normalized_user_id = user_id.strip().lower()
    no_id_values = {"", "<nil>", "nil", "none", "null", "all", "*"}
    if normalized_user_id in no_id_values:
        endpoint = "/users"
    else:
        endpoint = f"/users/{user_id.strip()}"
    result = call_user_api(path=endpoint, method="GET")
    return json.dumps(result, ensure_ascii=False)


@tool
def create_user_via_api(name: str, email: str) -> str:
    """Создает пользователя через HTTP API и возвращает JSON-ответ как строку."""
    payload = {"name": name, "email": email}
    result = call_user_api(path="/users", method="POST", payload=payload)
    return json.dumps(result, ensure_ascii=False)


def build_agent():
    model = os.getenv("OLLAMA_MODEL", "llama3.1")
    base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    no_proxy_value = os.getenv("NO_PROXY", "localhost,127.0.0.1")
    os.environ["NO_PROXY"] = no_proxy_value
    os.environ["no_proxy"] = no_proxy_value
    os.environ["OLLAMA_HOST"] = base_url
    chat_model = ChatOllama(model=model, base_url=base_url, temperature=0)

    return create_agent(
        model=chat_model,
        tools=[fetch_users_from_api, create_user_via_api],
        system_prompt=SYSTEM_PROMPT,
    )


def run_agent(query: str) -> str:
    agent = build_agent()
    try:
        result = agent.invoke({"messages": [{"role": "user", "content": query}]})
    except Exception as exc:  # noqa: BLE001
        return format_contract_response(
            query=query,
            tool_payload={"ok": False, "data": None, "error": f"agent runtime error: {exc}"},
        )
    messages = result["messages"]
    tool_payload = extract_last_tool_payload(messages)
    return format_contract_response(query=query, tool_payload=tool_payload)


def extract_last_tool_payload(messages: list[Any]) -> dict[str, Any] | None:
    for message in reversed(messages):
        if not isinstance(message, ToolMessage):
            continue

        content = message.content
        if isinstance(content, list):
            content = " ".join(
                chunk if isinstance(chunk, str) else json.dumps(chunk, ensure_ascii=False)
                for chunk in content
            )
        if not isinstance(content, str):
            content = json.dumps(content, ensure_ascii=False)

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {"ok": False, "data": None, "error": f"Некорректный JSON из tool: {content}"}
    return None


def format_contract_response(query: str, tool_payload: dict[str, Any] | None) -> str:
    action = query.strip() or "неизвестное действие"
    if tool_payload is None:
        status = "error"
        data = "-"
        errors = "Tool не был вызван"
    else:
        status = "success" if tool_payload.get("ok") else "error"
        data_value = tool_payload.get("data")
        data = json.dumps(data_value, ensure_ascii=False) if data_value is not None else "-"
        error_value = tool_payload.get("error")
        errors = str(error_value) if error_value else "-"

    return (
        f"Status: {status}\n"
        f"Action: {action}\n"
        f"Data: {data}\n"
        f"Errors: {errors}"
    )


if __name__ == "__main__":
    user_query = " ".join(sys.argv[1:]).strip() if len(sys.argv) > 1 else ""
    if not user_query:
        user_query = input("Введите запрос для агента: ").strip()
    if not user_query:
        print("Пустой запрос")
    else:
        answer = run_agent(user_query)
        print(answer)
