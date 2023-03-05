import typing


if typing.TYPE_CHECKING:
    from bot_app.app.web.app import Application


def setup_routes(app: "Application"):
    from bot_app.app.game_session.views import GameSessionListView

    app.router.add_view("/game-session.list", GameSessionListView)
