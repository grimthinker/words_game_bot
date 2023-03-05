import asyncio
import enum
import json
import random
from typing import Union, Optional

from app.game_session.models import SessionPlayer, Player, Word
from app.store.tg_api.dataclasses import Update


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
    return ((lst[x-1], lst[x]) for x in range(len(lst)))


def correct_text(update: Update):
    update.message.text = update.message.text.split("@")[0]


def check_word(proposed_word: str, previous_word: str):
    # Rules on how to decide whether we let the word to the vote
    return proposed_word[0] == previous_word[-1]


def judge_word(word: str) -> int:
    # Rules on how to appraise the given word in points equivalent
    return 100


def list_results(players: list[SessionPlayer]) -> str:
    string = ""
    for player in players:
        string += str(player.player_id)
        string += ": "
        string += str(player.points)
        string += " points; "
    return string

class MessageHelper():
    initial = "Commands: /start, /participate, /launch, /yes, /no, /end"
    already_started = "Game's already started"
    no_session = "No running game session, start a new one using /start"
    cant_join_now = "Can't join the game session now, wait till a new session starts"
    already_launched = "Game's already launched"
    too_dew_players = "Too few players, wait for another one"
    launched = "The game has started!"
    game_is_not_launched = "Launch the game first"
    no_word_to_vote = "We need to get a word first"
    time_for_word_ended = "Time has ended, no word has been proposed"
    time_for_vote_ended = "Time to check the vote results"
    all_players_voted = "All players have voted, lets check the results"
    everyone_voted = "Everyone has voted, let's check the result"

    @staticmethod
    def started(update: Update):
        return f"{update.message.user.username} has joined the game. Now wait for players to /participate, then /launch the game"

    @staticmethod
    def already_participates(update: Update):
        return f"{update.message.user.username} already in the game"

    @staticmethod
    def joined(update: Update):
        return f"{update.message.user.username} has joined the game"

    @staticmethod
    def not_creator_to_launch(update: Update):
        return f"{update.message.user.username} is not the creator of the session to launch it"

    @staticmethod
    def wrong_player_turn(update: Update):
        return f"Now is not {update.message.user.username} turn"

    @staticmethod
    def word_doesnt_fit(update: Update):
        return f"The word {update.message.text} does not fit"

    @staticmethod
    def word_proposed(update: Update):
        return f"{update.message.user.username} proposes a word: '{update.message.text}'"

    @staticmethod
    def cant_vote(update: Update):
        return f"{update.message.user.username} cannot vote"

    @staticmethod
    def already_voted(update: Update):
        return f"{update.message.user.username} has already voted"

    @staticmethod
    def on_someones_vote(update: Update, word: Word):
        return f"{update.message.user.username} votes '{update.message.text}' for '{word.word}'"

    @staticmethod
    def game_results(session_players: list[SessionPlayer]):
        return f"Game ended. Results: " + list_results(session_players)

    @staticmethod
    def announce_winner(player: Player):
        return f"The winner is {player.name}!"

    @staticmethod
    def remind_word_for_next(word: Word, player: Player):
        return f"The word: '{word.word}'. Player {player.name}, propose your word!"

    @staticmethod
    def vote_for_word(word: Word):
        return f"The proposed word: '{word.word}'. Vote /yes or /no if it's an existing word!"

    @staticmethod
    def vote_result_negative(word: Word, player: Player):
        return f"{word.word} is not counted as a word! {player.name} is lost"

    @staticmethod
    def vote_result_positive(word: Word, player: Player, points: int):
        return f"{word.word} is counted as a word! {player.name} has earned {points} points"
