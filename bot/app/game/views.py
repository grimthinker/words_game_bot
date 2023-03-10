from aiohttp_apispec import request_schema, json_schema, response_schema, docs

from bot_app.app.game_session.schemes import GameSessionListSchema
from bot_app.app.web.app import View
from bot_app.app.web.utils import json_response
from bot_app.app.web.mixins import AuthRequiredMixin


class GameSessionListView(AuthRequiredMixin, View):
    @response_schema(GameSessionListSchema)
    async def get(self):
        game_sessions = await self.store.game_sessions.get_sessions()
        return json_response(
            data=GameSessionListSchema().dump({"game_sessions": game_sessions})
        )
