import typing
from dataclasses import dataclass

import yaml

if typing.TYPE_CHECKING:
    from app.web.app import Application


@dataclass
class SessionConfig:
    key: str


@dataclass
class AdminConfig:
    email: str
    password: str


@dataclass
class RabbitMQConfig:
    host: str
    port: int


@dataclass
class BotConfig:
    vk_token: str
    tg_token: str
    group_id: int
    api: str


@dataclass
class GameConfig:
    word_wait_time: int
    vote_wait_time: int
    random_start: bool


@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = "postgres"
    database: str = "project"


@dataclass
class Config:
    admin: AdminConfig
    session: SessionConfig = None
    rabbitmq: RabbitMQConfig = None
    bot: BotConfig = None
    game: GameConfig = None
    database: DatabaseConfig = None


def setup_config(app: "Application", config_path: str):
    with open(config_path, "r") as f:
        raw_config = yaml.safe_load(f)

    app.config = Config(
        session=SessionConfig(
            key=raw_config["session"]["key"],
        ),
        admin=AdminConfig(
            email=raw_config["admin"]["email"],
            password=raw_config["admin"]["password"],
        ),
        game=GameConfig(
            word_wait_time=raw_config["game"]["word_wait_time"],
            vote_wait_time=raw_config["game"]["vote_wait_time"],
            random_start=raw_config["game"]["random_start"],
        ),
        rabbitmq=RabbitMQConfig(
            host=raw_config["rabbitmq"]["host"],
            port=raw_config["rabbitmq"]["port"],
        ),
        bot=BotConfig(
            vk_token=raw_config["bot"]["vk_token"],
            tg_token=raw_config["bot"]["tg_token"],
            group_id=raw_config["bot"]["group_id"],
            api=raw_config["bot"]["api"],
        ),
        database=DatabaseConfig(**raw_config["database"]),
    )
