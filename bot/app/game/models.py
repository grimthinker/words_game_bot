import enum
from dataclasses import dataclass, field
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

    SESSION_NEEDED = 11  # not state, for chat filtering


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
