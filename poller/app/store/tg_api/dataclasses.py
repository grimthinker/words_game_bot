from dataclasses import dataclass
from typing import Optional, Union


@dataclass
class UpdateUser:
    id: int
    is_bot: bool
    first_name: str
    username: str


@dataclass
class UpdateMessage:
    user: Optional[UpdateUser]
    text: str
    id: int
    chat_id: int
    date: int


@dataclass
class Update:
    id: int
    message: UpdateMessage
