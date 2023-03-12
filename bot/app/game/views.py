from aiohttp_apispec import request_schema, json_schema, response_schema, docs, querystring_schema

from app.web.app import View
from app.web.utils import json_response
from app.web.mixins import AuthRequiredMixin
from app.game.schemes import GameRulesSchema, GameSessionSchema, GameSessionListSchema, TimeSettingsSchema, GameRulesIdSchema, TimeSettingsIdSchema

from aiohttp.web_exceptions import (
    HTTPConflict,
    HTTPUnauthorized,
    HTTPBadRequest,
    HTTPNotFound,
)

from app.game.models import GameRulesModel


class GameSessionListView(AuthRequiredMixin, View):
    @docs(tags=["game sessions"], summary="List game sessions", description="Shows the list of game sessions")
    @response_schema(GameSessionListSchema, 200)
    async def get(self):
        async with self.database.session.begin() as db_session:
            game_sessions = await self.store.game_sessions.get_sessions(db_session)
            game_sessions = {"game_sessions": [
                GameSessionSchema().dump(session) for session in game_sessions
            ]}
            return json_response(
                data=game_sessions
            )


class GameRulesView(AuthRequiredMixin, View):
    @docs(tags=["game rules"], summary="Game rules", description="Show game rules for a session")
    @querystring_schema(GameRulesIdSchema)
    @response_schema(GameRulesSchema, 200)
    async def get(self):
        try:
            session_id = int(self.request.query["session_id"])
        except:
            raise HTTPBadRequest
        async with self.database.session.begin() as db_session:
            rules = await self.store.game_rules.get_rules(db_session, session_id)
            if not rules:
                raise HTTPNotFound
            return json_response(
                data=GameRulesSchema().dump(rules)
            )


    @docs(tags=["game rules"], summary="Game rules", description="Set game rules for a session")
    @request_schema(GameRulesSchema)
    @response_schema(GameRulesSchema, 200)
    async def post(self):
        session_id = self.data["session_id"]
        async with self.database.session.begin() as db_session:
            rules = await self.store.game_rules.get_rules(db_session, session_id)
            if not rules:
                raise HTTPNotFound

            params = dict()
            for param in self.data:
                if param in GameRulesModel.field_names and param != "session_id":
                    params[param] = self.data[param]
            if params:
                await self.store.game_rules.set_rules(db_session, session_id, **params)
            params["session_id"] = session_id

            rules = await self.store.game_rules.get_rules(db_session, session_id)
        return json_response(
            data=GameRulesSchema().dump(rules)
        )


class TimeSettingsView(AuthRequiredMixin, View):
    @docs(tags=["time settings"], summary="Time settings", description="Show time settings")
    @querystring_schema(TimeSettingsIdSchema)
    @response_schema(TimeSettingsSchema, 200)
    async def get(self):
        try:
            time_settings_id = int(self.request.query["id"])
        except:
            raise HTTPBadRequest
        async with self.database.session.begin() as db_session:
            settings = await self.store.game_rules.get_time_settings(db_session, time_settings_id)
            if not settings:
                raise HTTPNotFound
            settings = TimeSettingsSchema().dump(settings)
            return json_response(
                data=settings
            )

    @docs(tags=["time settings"], summary="Time settings", description="Set time settings")
    @request_schema(TimeSettingsSchema)
    @response_schema(TimeSettingsSchema, 200)
    async def post(self):
        time_settings_id = self.data["id"]
        async with self.database.session.begin() as db_session:
            settings = await self.store.game_rules.get_time_settings(db_session, time_settings_id)
            if not settings:
                raise HTTPNotFound

            params = dict()
            for param in self.data:
                if param in ["wait_word_time", "wait_vote_time"]:
                    params[param] = self.data[param]
            if params:
                await self.store.game_rules.update_time_settings(db_session, time_settings_id, **params)
            params["id"] = time_settings_id
            settings = await self.store.game_rules.get_time_settings(db_session, time_settings_id)
        return json_response(
            data=TimeSettingsSchema().dump(settings)
        )
