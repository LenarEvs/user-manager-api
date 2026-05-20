from fastapi import FastAPI, HTTPException, Response, status

from app.models import User, UserCreate, UserUpdate
from app.store import UserStore

app = FastAPI(title="User Manager API", version="0.1.0")
store = UserStore()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/users", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate) -> User:
    return store.create(payload)


@app.get("/users", response_model=list[User])
def list_users() -> list[User]:
    return store.list()


@app.get("/users/{user_id}", response_model=User)
def get_user(user_id: int) -> User:
    user = store.get(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@app.patch("/users/{user_id}", response_model=User)
def update_user(user_id: int, payload: UserUpdate) -> User:
    user = store.update(user_id, payload)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int) -> Response:
    deleted = store.delete(user_id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
