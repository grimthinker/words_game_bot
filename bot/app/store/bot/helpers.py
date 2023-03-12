import asyncio
import random
from typing import Union

from app.base.dataclasses import Update
from app.game.models import (
    SessionPlayer,
    Player,
    Word,
    GameSession,
    StatesEnum,
    GameRules,
)


class AsyncTimer:
    def __init__(self, timeout, callback, callback_params: dict, app: "Application"):
        self._timeout = timeout
        self._callback = callback
        self._callback_params = callback_params
        self.app = app
        self._task = asyncio.ensure_future(self._job())

    async def _job(self):
        await asyncio.sleep(self._timeout)
        async with self.app.database.session.begin() as db_session:
            await self._callback(db_session, **self._callback_params)

    def cancel(self):
        self._task.cancel()


def remove_timer(timers: dict, key: int):
    timer_to_stop = timers.get(key)
    if timer_to_stop:
        timer_to_stop.cancel()
        timers.pop(key)


def generate_some_order(lst: list):
    random.shuffle(lst)
    return ((lst[x - 1], lst[x]) for x in range(len(lst)))


def correct_text(update: Update) -> str:
    update.message.text = update.message.text.split("@")[0]


def check_word(proposed_word: str, previous_word: str, game_rules: GameRules) -> bool:
    is_fit = proposed_word[0] == previous_word[-1]
    return is_fit


def judge_word(word: str, game_rules: GameRules) -> int:
    # Rules on how to appraise the given word in points equivalent
    return 100


def is_session_running(session: GameSession = None) -> bool:
    return session and session.state != StatesEnum.ENDED.value


def list_results(players: list[SessionPlayer]) -> str:
    string = ""
    for player in players:
        string += str(player.player_id)
        string += ": "
        string += str(player.points)
        string += " points; "
    return string
