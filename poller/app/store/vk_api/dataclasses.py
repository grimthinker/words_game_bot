from dataclasses import dataclass
from typing import Optional, Union


@dataclass
class UpdateUser:
    id: int
    username: str


@dataclass
class UpdateMessage:
    user: Optional[UpdateUser]
    text: str
    id: int
    chat_id: int


@dataclass
class Update:
    id: int
    message: UpdateMessage
