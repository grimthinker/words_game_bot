import json
from typing import Any, Optional, Union

from aiohttp.web import json_response as aiohttp_json_response
from aiohttp.web_response import Response

from app.store.tg_api.dataclasses import Update as tgUpdate, UpdateMessage as tgMessage, UpdateUser as tgUser
from app.store.vk_api.dataclasses import Update as vkUpdate, UpdateMessage as vkMessage, UpdateUser as vkUser


def json_response(data: Any = None, status: str = "ok") -> Response:
    if data is None:
        data = {}
    return aiohttp_json_response(
        data={
            "status": status,
            "data": data,
        }
    )


def error_json_response(
    http_status: int,
    status: str = "error",
    message: Optional[str] = None,
    data: Optional[dict] = None,
):
    if data is None:
        data = {}
    return aiohttp_json_response(
        status=http_status,
        data={
            "status": status,
            "message": str(message),
            "data": data,
        },
    )


def vk_make_update_from_raw(raw_update: dict) -> vkUpdate:
    print("wawwaar")
    text = raw_update["object"]["message"]["text"].split()[-1]
    update = vkUpdate(id=raw_update["event_id"],
                      message=vkMessage(user=vkUser(id=raw_update["object"]["message"]["from_id"],
                                                    username=str(raw_update["object"]["message"]["from_id"])),
                                        chat_id=raw_update["object"]["message"]["peer_id"],
                                        id=raw_update["event_id"],
                                        text=text))
    return update


def tg_make_update_from_raw(raw_update: dict) -> tgUpdate:
    update = tgUpdate(
        id=raw_update["update_id"],
        message=tgMessage(
            user=tgUser(
                id=raw_update["message"]["from"]["id"],
                is_bot=raw_update["message"]["from"]["is_bot"],
                first_name=raw_update["message"]["from"]["first_name"],
                username=raw_update["message"]["from"]["username"]),
            text=raw_update["message"]["text"],
            id=raw_update["message"]["message_id"],
            chat_id=raw_update["message"]["chat"]["id"],
            date=raw_update["message"]["date"],
        ))
    return update


class KeyboardHelper:
    @classmethod
    def _button(
        cls,
        label: str,
        payload: Union[int, str, None] = None,
        color: Optional[str] = None,
    ) -> dict:
        button = {"action": {"type": "text", "label": label}}
        if payload:
            button["action"]["payload"] = payload
        if color:
            button["color"] = color
        return button

    @classmethod
    def _keyboard(cls, buttons: list[list[dict]]) -> str:
        keyboard = {"one_time": False, "buttons": buttons, "inline": False}
        return json.dumps(keyboard)

    @classmethod
    def generate_helping_keyboard(cls):
        buttons = [
            [cls._button("/start", payload="{}"), cls._button("/launch", payload="{}"), cls._button("/yes", payload="{}")],
            [cls._button("/participate", payload="{}"), cls._button("/end", payload="{}"), cls._button("/no", payload="{}")],
        ]
        return cls._keyboard(buttons=buttons)
