from marshmallow import Schema, fields


class PlayerSchema(Schema):
    id = fields.Int()
    name = fields.Str()


class GameSessionSchema(Schema):
    id = fields.Int(required=False)
    chat_id = fields.Int()
    creator = fields.Nested("PlayerSchema", many=False)
    state = fields.Int()
    players = fields.Nested("PlayerSchema", many=True)


class GameSessionListSchema(Schema):
    game_sessions = fields.Nested("GameSessionSchema", many=True)


class TimeSettingsSchema(Schema):
    id = fields.Int(required=True, load_only=True)
    name = fields.Str(required=False, load_only=True)
    wait_word_time = fields.Int()
    wait_vote_time = fields.Int()


class GameRulesSchema(Schema):
    session_id = fields.Int(required=True, load_only=True)
    lives = fields.Int(required=False)
    max_diff_rule = fields.Boolean(required=False)
    max_diff_val = fields.Int(required=False)
    min_diff_rule = fields.Boolean(required=False)
    min_diff_val = fields.Int(required=False)
    max_long_rule = fields.Boolean(required=False)
    max_long_val = fields.Int(required=False)
    min_long_rule = fields.Boolean(required=False)
    min_long_val = fields.Int(required=False)
    similarity_valued = fields.Boolean(required=False)
    short_on_time = fields.Boolean(required=False)
    req_vote_percentage = fields.Float(required=False)
    time_settings_id = fields.Int(required=False)
    custom_vote_time = fields.Int(required=False)
    custom_word_time = fields.Int(required=False)

class TimeSettingsIdSchema(Schema):
    id = fields.Int()

class GameRulesIdSchema(Schema):
    session_id = fields.Int()
