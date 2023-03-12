import typing


if typing.TYPE_CHECKING:
    from app.web.app import Application


def setup_routes(app: "Application"):
    from app.game.views import GameSessionListView
    from app.game.views import GameRulesView
    from app.game.views import TimeSettingsView

    app.router.add_view("/game-session.list", GameSessionListView)
    app.router.add_view("/game-rules", GameRulesView)
    app.router.add_view("/time-settings", TimeSettingsView)
