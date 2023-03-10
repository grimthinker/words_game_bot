import typing
from dataclasses import dataclass

import yaml

if typing.TYPE_CHECKING:
    from app.web.app import Application


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
class Config:
    rabbitmq: RabbitMQConfig = None
    bot: BotConfig = None


def setup_config(app: "Application", config_path: str):
    with open(config_path, "r") as f:
        raw_config = yaml.safe_load(f)

    app.config = Config(
        rabbitmq=RabbitMQConfig(
            host=raw_config["rabbitmq"]["host"],
            port=raw_config["rabbitmq"]["port"],
        ),
        bot=BotConfig(
            vk_token=raw_config["bot"]["vk_token"],
            tg_token=raw_config["bot"]["tg_token"],
            group_id=raw_config["bot"]["group_id"],
            api=raw_config["bot"]["api"],
        )
    )
