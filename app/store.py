from typing import Dict

from app.models import User, UserCreate, UserUpdate


class UserStore:
    def __init__(self) -> None:
        self._users: Dict[int, User] = {}
        self._next_id = 1

    def create(self, payload: UserCreate) -> User:
        user = User(id=self._next_id, name=payload.name, email=payload.email)
        self._users[user.id] = user
        self._next_id += 1
        return user

    def list(self) -> list[User]:
        return list(self._users.values())

    def get(self, user_id: int) -> User | None:
        return self._users.get(user_id)

    def update(self, user_id: int, payload: UserUpdate) -> User | None:
        user = self.get(user_id)
        if user is None:
            return None

        updated = user.model_copy(
            update=payload.model_dump(exclude_unset=True),
        )
        self._users[user_id] = updated
        return updated

    def delete(self, user_id: int) -> bool:
        if user_id not in self._users:
            return False

        del self._users[user_id]
        return True
