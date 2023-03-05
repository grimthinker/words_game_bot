from marshmallow import Schema, fields


class GameSessionSchema(Schema):
    id = fields.Int(required=False)
    chat_id = fields.Int(required=True)


class GameSessionListSchema(Schema):
    sessions = fields.Nested(GameSessionSchema, many=True)
