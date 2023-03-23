import json
from typing import Any, Optional, Union

from aiohttp.web import json_response as aiohttp_json_response
from aiohttp.web_response import Response

from app.base.dataclasses import UpdateUser, UpdateMessage, Update
from app.store.tg_api.dataclasses import TGUpdateUser, TGUpdateMessage, TGUpdate
from app.game.models import (
    SessionPlayer,
    Player,
    Word,
    GameSession,
    StatesEnum,
    GameRules,
)

from app.store.bot.helpers import list_results


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


def _build_query(host: str, method: str, params: dict) -> str:
    url = host + method + "?"
    url += "&".join([f"{k}={v}" for k, v in params.items()])
    return url


def vk_make_update_from_raw(raw_update: dict) -> Update:
    text = raw_update["object"]["message"]["text"].split()[-1]
    update = Update(
        id=raw_update["event_id"],
        message=UpdateMessage(
            user=UpdateUser(
                id=raw_update["object"]["message"]["from_id"],
                username=str(raw_update["object"]["message"]["from_id"]),
            ),
            chat_id=raw_update["object"]["message"]["peer_id"],
            id=raw_update["event_id"],
            text=text,
        ),
    )
    return update


def tg_make_update_from_raw(raw_update: dict) -> Update:
    try:
        update = TGUpdate(
            id=raw_update["update_id"],
            message=TGUpdateMessage(
                user=TGUpdateUser(
                    id=raw_update["message"]["from"]["id"],
                    is_bot=raw_update["message"]["from"]["is_bot"],
                    first_name=raw_update["message"]["from"]["first_name"],
                    username=raw_update["message"]["from"]["username"],
                ),
                text=raw_update["message"]["text"],
                id=raw_update["message"]["message_id"],
                chat_id=raw_update["message"]["chat"]["id"],
                date=raw_update["message"]["date"],
            ),
        )
        return update
    except:
        pass


class KeyboardHelper:
    def __init__(self, external_api):
        self.external_api = external_api

    def _button(
        self,
        label: str,
        payload: Union[int, str, None] = None,
        color: Optional[str] = None,
    ) -> dict:
        if self.external_api == "vk":
            button = {"action": {"type": "text", "label": label}}
            if payload:
                button["action"]["payload"] = payload
            if color:
                button["color"] = color
        else:
            button = {"text": label}
        return button

    def _keyboard(self, buttons: list) -> str:
        if self.external_api == 'vk':
            keyboard = {"one_time": False, "buttons": buttons, "inline": False}
        else:
            keyboard = {"keyboard": buttons}
        return json.dumps(keyboard)

    def generate_helping_keyboard(self):
        buttons = [
            [
                self._button("/start", payload="{}"),
                self._button("/launch", payload="{}"),
                self._button("/yes", payload="{}"),
            ],
            [
                self._button("/participate", payload="{}"),
                self._button("/end", payload="{}"),
                self._button("/no", payload="{}"),
            ],
            [
                self._button("/info", payload="{}"),
            ],
        ]
        return self._keyboard(buttons=buttons)

    def generate_settings_keyboard(self):
        buttons = [
            [
                self._button("/similarity_valued", payload="{}"),
                self._button("/similarity_not_valued", payload="{}"),
            ],
            [
                self._button("/short_on_time", payload="{}"),
                self._button("/not_short_on_time", payload="{}"),
            ],
            [
                self._button("/launch", payload="{}"),
            ],
        ]
        return self._keyboard(buttons=buttons)



class MessageHelper:
    initial = "Commands: /start, /participate, /launch, /yes, /no, /end"
    already_started = "Game's already started"
    no_session = "No running game session, start a new one using /start"
    cant_join_now = "Can't join the game session now, wait till a new session starts"
    cant_end = "Only the one started the game can stop it "
    already_launched = "Game's already launched"
    too_few_players = "Too few players, wait for new ones"
    too_much_players = "Too much players, wait for new game session"
    launched = "The game has started!"
    game_is_not_launched = "Launch the game first"
    no_word_to_vote = "We need to get a word first"
    time_for_word_ended = "Time has ended, no word has been proposed"
    time_for_vote_ended = "Time to check the vote results"
    all_players_voted = "All players have voted, lets check the results"
    everyone_voted = "Everyone has voted, let's check the result"
    no_session_in_db = "No session in database, can't show results"

    @staticmethod
    def started(update: Union[Update, TGUpdate]) -> str:
        return f"{update.message.user.username} has joined the game. Now wait for players to /participate, then /launch the game"

    @staticmethod
    def already_participates(update: Union[Update, TGUpdate]) -> str:
        return f"{update.message.user.username} already in the game"

    @staticmethod
    def joined(update: Union[Update, TGUpdate]) -> str:
        return f"{update.message.user.username} has joined the game"

    @staticmethod
    def not_creator_to_launch(update: Union[Update, TGUpdate]) -> str:
        return f"{update.message.user.username} is not the creator of the session to launch it"

    @staticmethod
    def wrong_player_turn(update: Union[Update, TGUpdate]) -> str:
        return f"Now is not {update.message.user.username} turn"

    @staticmethod
    def used_word(update: Union[Update, TGUpdate]) -> str:
        return f"The word '{update.message.text}' has already been used earlier"

    @staticmethod
    def too_short_word(update: Union[Update, TGUpdate]) -> str:
        return f"The word '{update.message.text}' is too short"

    @staticmethod
    def word_doesnt_fit(update: Union[Update, TGUpdate]) -> str:
        return f"The word {update.message.text} does not fit"

    @staticmethod
    def word_proposed(update: Union[Update, TGUpdate]) -> str:
        return (
            f"{update.message.user.username} proposes a word: '{update.message.text}'"
        )

    @staticmethod
    def cant_vote(update: Union[Update, TGUpdate]) -> str:
        return f"{update.message.user.username} cannot vote"

    @staticmethod
    def already_voted(update: Union[Update, TGUpdate], word: Word) -> str:
        return f"{update.message.user.username} has already voted {update.message.text} for the word '{word.word}'"

    @staticmethod
    def on_someones_revote(update: Union[Update, TGUpdate], word: Word) -> str:
        return f"{update.message.user.username} changes the vote to '{update.message.text}' for the word '{word.word}'"

    @staticmethod
    def on_someones_vote(update: Union[Update, TGUpdate], word: Word) -> str:
        return f"{update.message.user.username} votes '{update.message.text}' for the word '{word.word}'"

    @staticmethod
    def game_results(session_players: list[SessionPlayer]) -> str:
        return f"Game ended. Results: " + list_results(session_players)

    @staticmethod
    def last_game_results(
        session: GameSession, session_players: list[SessionPlayer]
    ) -> str:
        return f"Results: " + list_results(session_players)

    @staticmethod
    def announce_winner(player: Player) -> str:
        return f"The winner is {player.name}!"

    @staticmethod
    def remind_word_for_next(word: Word, player: Player) -> str:
        return f"The word: '{word.word}'. Player {player.name}, propose your word!"

    @staticmethod
    def vote_for_word(word: Word) -> str:
        return f"The proposed word: '{word.word}'. Vote /yes or /no if it's an existing word!"

    @staticmethod
    def vote_result_negative(word: Word, player: Player) -> str:
        return f"{word.word} is not counted as a word! {player.name} is lost"

    @staticmethod
    def vote_result_positive(word: Word, player: Player, points: int) -> str:
        return f"{word.word} is counted as a word! {player.name} has earned {points} points"
