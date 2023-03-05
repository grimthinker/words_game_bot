import typing
from dataclasses import dataclass

import yaml

if typing.TYPE_CHECKING:
    from bot_app.app.web.app import Application


@dataclass
class BotConfig:
    vk_token: str
    tg_token: str
    group_id: int


@dataclass
class Config:
    bot: BotConfig = None


def setup_config(app: "Application", config_path: str):
    with open(config_path, "r") as f:
        raw_config = yaml.safe_load(f)

    app.config = Config(
        bot=BotConfig(
            vk_token=raw_config["bot"]["vk_token"],
            tg_token=raw_config["bot"]["tg_token"],
            group_id=raw_config["bot"]["group_id"],
        )
    )
