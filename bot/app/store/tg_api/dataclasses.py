from dataclasses import dataclass
from typing import Optional, Union

from app.base.dataclasses import UpdateUser, UpdateMessage, Update


@dataclass
class TGUpdateUser(UpdateUser):
    is_bot: bool
    first_name: str


@dataclass
class TGUpdateMessage(UpdateMessage):
    user: Optional[TGUpdateUser]
    date: int


@dataclass
class TGUpdate(Update):
    message: TGUpdateMessage
