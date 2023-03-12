import enum
from dataclasses import dataclass, field, fields
from typing import Optional, List

from app.store.database.sqlalchemy_base import db
from sqlalchemy.orm import relationship, backref
from sqlalchemy import (
    Column,
    BigInteger,
    Boolean,
    ForeignKey,
    Integer,
    Text,
    Table,
    DateTime,
    Float,
    func,
)


@dataclass
class Chat:
    id: int


@dataclass
class Player:
    id: int
    name: str


@dataclass
class SessionPlayer:
    player_id: int
    session_id: str
    points: int
    is_dropped_out: bool
    next_player_id: int


@dataclass
class Word:
    id: int
    word: str
    session_id: int
    proposed_by: int
    approved: Optional[bool]
    previous_word_id: int


@dataclass
class GameSession:
    id: int
    chat_id: int
    creator: Player
    state: int
    players: List[Player] = field(default_factory=list)
    last_word: Optional[str] = None
    time_updated: Optional[str] = None


@dataclass
class TimeSettings:
    id: int
    name: str
    wait_word_time: int
    wait_vote_time: int


@dataclass
class GameRules:
    session_id: int
    max_diff_rule: bool
    max_diff_val: int
    min_diff_rule: bool
    min_diff_val: int
    max_long_rule: bool
    max_long_val: int
    min_long_rule: bool
    min_long_val: int
    similarity_valued: bool
    short_on_time: bool
    req_vote_percentage: float
    time_settings: TimeSettings
    custom_vote_time: Optional[int] = None
    custom_word_time: Optional[int] = None


class ChatModel(db):
    __tablename__ = "chats"
    id = Column(BigInteger, primary_key=True)


class WordVotes(db):
    __tablename__ = "votes"
    session_word = Column(
        BigInteger, ForeignKey("session_words.id", ondelete="CASCADE"), primary_key=True
    )
    player_id = Column(
        BigInteger, ForeignKey("players.id", ondelete="CASCADE"), primary_key=True
    )
    vote = Column(Boolean, nullable=False)


class SessionWords(db):
    __tablename__ = "session_words"
    id = Column(BigInteger, primary_key=True)
    word = Column(Text, nullable=False)
    proposed_by = Column(
        BigInteger, ForeignKey("players.id", ondelete="CASCADE"), nullable=False
    )
    approved = Column(Boolean, nullable=True)
    previous_word = Column(
        BigInteger, ForeignKey("session_words.id", ondelete="SET NULL")
    )
    session_id = Column(
        BigInteger, ForeignKey("game_sessions.id", ondelete="CASCADE"), nullable=False
    )

    @staticmethod
    def to_dc(model) -> Word:
        word = Word(
            id=model.id,
            word=model.word,
            session_id=model.session_id,
            proposed_by=model.proposed_by,
            previous_word_id=model.previous_word,
            approved=model.approved,
        )
        return word


class StatesEnum(enum.Enum):
    PREPARING = 0
    WAITING_WORD = 2
    VOTE = 3
    ENDED = 9


class GameSessionModel(db):
    __tablename__ = "game_sessions"
    id = Column(BigInteger, primary_key=True)
    chat_id = Column(
        BigInteger, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False
    )
    creator_id = Column(
        BigInteger, ForeignKey("players.id", ondelete="CASCADE"), nullable=False
    )
    state = Column(Integer, nullable=False)
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    association_players_sessions = relationship(
        "PlayersSessions", back_populates="sessions"
    )

    @staticmethod
    def to_dc(model, creator: Player, players: List[Player]) -> GameSession:
        session = GameSession(
            id=model.id,
            chat_id=model.chat_id,
            state=model.state,
            creator=creator,
            players=players,
        )
        return session


class PlayersSessions(db):
    __tablename__ = "association_players_sessions"
    player_id = Column(
        BigInteger, ForeignKey("players.id", ondelete="CASCADE"), primary_key=True
    )
    session_id = Column(
        BigInteger, ForeignKey("game_sessions.id", ondelete="CASCADE"), primary_key=True
    )
    points = Column(Integer, nullable=False, default=0)
    is_dropped_out = Column(Boolean, nullable=False, default=False)
    next_player_id = Column(BigInteger, ForeignKey("players.id", ondelete="SET NULL"))

    player = relationship(
        "PlayerModel",
        backref="player_in_session",
        foreign_keys="[PlayersSessions.player_id]",
    )
    next_player = relationship(
        "PlayerModel",
        backref="previous_player",
        foreign_keys="[PlayersSessions.next_player_id]",
    )
    sessions = relationship(
        "GameSessionModel", back_populates="association_players_sessions"
    )

    @staticmethod
    def to_dc(model) -> SessionPlayer:
        session_player = SessionPlayer(
            player_id=model.player_id,
            session_id=model.session_id,
            points=model.points,
            is_dropped_out=model.is_dropped_out,
            next_player_id=model.next_player_id,
        )
        return session_player


class PlayerModel(db):
    __tablename__ = "players"
    id = Column(BigInteger, primary_key=True)
    name = Column(Text, nullable=False, default="no name")


class TimeSettingsModel(db):
    __tablename__ = "time_settings"
    id = Column(BigInteger, primary_key=True)
    name = Column(Text, nullable=False, default="basic")
    wait_word_time = Column(BigInteger, nullable=False, default=40)
    wait_vote_time = Column(BigInteger, nullable=False, default=25)

    @staticmethod
    def to_dc(model) -> TimeSettings:
        time_settings = TimeSettings(
            id=model.id,
            name=model.name,
            wait_word_time=model.wait_word_time,
            wait_vote_time=model.wait_vote_time,
        )
        return time_settings


class GameRulesModel(db):
    __tablename__ = "game_rules"
    field_names = [f.name for f in fields(GameRules)]
    session_id = Column(
        BigInteger, ForeignKey("game_sessions.id", ondelete="CASCADE"), primary_key=True
    )
    max_diff_rule = Column(Boolean, nullable=False, default=False)
    max_diff_val = Column(BigInteger, nullable=False, default=15)
    min_diff_rule = Column(Boolean, nullable=False, default=False)
    min_diff_val = Column(BigInteger, nullable=False, default=1)
    max_long_rule = Column(Boolean, nullable=False, default=False)
    max_long_val = Column(BigInteger, nullable=False, default=20)
    min_long_rule = Column(Boolean, nullable=False, default=False)
    min_long_val = Column(BigInteger, nullable=False, default=2)
    custom_vote_time = Column(BigInteger, nullable=True, default=50)
    custom_word_time = Column(BigInteger, nullable=True, default=50)
    similarity_valued = Column(Boolean, nullable=False, default=False)
    short_on_time = Column(Boolean, nullable=False, default=False)
    req_vote_percentage = Column(Float, nullable=False, default=0.5)
    time_settings_id = Column(
        BigInteger, ForeignKey("time_settings.id", ondelete="CASCADE"), nullable=False
    )

    @staticmethod
    def to_dc(model, time_settings: TimeSettings) -> GameRules:
        game_rules = GameRules(
            session_id=model.session_id,
            max_diff_rule=model.max_diff_rule,
            max_diff_val=model.max_diff_val,
            min_diff_rule=model.min_diff_rule,
            min_diff_val=model.min_diff_val,
            max_long_rule=model.max_long_rule,
            max_long_val=model.max_long_val,
            min_long_rule=model.min_long_rule,
            min_long_val=model.min_long_val,
            custom_vote_time=model.custom_vote_time,
            custom_word_time=model.custom_word_time,
            similarity_valued=model.similarity_valued,
            short_on_time=model.short_on_time,
            req_vote_percentage=model.req_vote_percentage,
            time_settings=time_settings,
        )
        return game_rules
