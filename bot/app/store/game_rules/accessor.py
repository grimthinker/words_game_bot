from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.base.base_accessor import BaseAccessor
from app.game.models import GameRulesModel, GameRules, TimeSettingsModel, TimeSettings


class GameRulesAccessor(BaseAccessor):
    basic_time_settings_id = 1
    shortened_time_settings_id = 2

    async def connect(self, app: "Application"):
        async with self.app.database.session() as db_session:
            basic_time_settings = await self.get_time_settings(
                db_session, self.basic_time_settings_id
            )
            shortened_time_settings = await self.get_time_settings(
                db_session, self.shortened_time_settings_id
            )
            if not basic_time_settings:
                time_settings = TimeSettingsModel(
                    id=self.basic_time_settings_id
                )  # adding the basic time settings
                db_session.add(time_settings)
            if not shortened_time_settings:
                time_settings = TimeSettingsModel(
                    id=self.shortened_time_settings_id,
                    name="shortened time",
                    wait_word_time=12,
                    wait_vote_time=15,
                )
                db_session.add(time_settings)
            await db_session.commit()

    async def create_rules(
        self, db_session: AsyncSession, session_id: int, time_settings_id: int
    ):
        game_rules = GameRulesModel(
            session_id=session_id, time_settings_id=time_settings_id
        )
        db_session.add(game_rules)
        time_settings = await self.get_time_settings(
            db_session, game_rules.time_settings_id
        )
        return GameRulesModel.to_dc(game_rules, time_settings)

    async def set_rules(self, db_session: AsyncSession, session_id: int, **kwargs):
        stmt = (
            update(GameRulesModel)
            .filter(GameRulesModel.session_id == session_id)
            .values(kwargs)
        )
        await db_session.execute(stmt)

    async def get_rules(
        self, db_session: AsyncSession, session_id: int
    ) -> Optional[GameRules]:
        stmt = select(GameRulesModel).filter(GameRulesModel.session_id == session_id)
        result = await db_session.execute(stmt)
        game_rules = result.scalars().first()
        time_settings = await self.get_time_settings(
            db_session, game_rules.time_settings_id
        )
        return GameRulesModel.to_dc(game_rules, time_settings) if game_rules else None

    async def get_time_settings(
        self, db_session: AsyncSession, time_settings_id: int
    ) -> Optional[TimeSettings]:
        stmt = select(TimeSettingsModel).filter(
            TimeSettingsModel.id == time_settings_id
        )
        result = await db_session.execute(stmt)
        time_settings = result.scalars().first()
        return TimeSettingsModel.to_dc(time_settings) if time_settings else None

    async def update_time_settings(
        self, db_session: AsyncSession, time_settings_id: int, **values
    ) -> TimeSettings:
        stmt = (
            update(TimeSettingsModel)
            .filter(TimeSettingsModel.id == time_settings_id)
            .values(values)
        )
        await db_session.execute(stmt)
