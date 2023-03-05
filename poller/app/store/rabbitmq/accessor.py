import asyncio
from aio_pika import Message, connect

from app.base.base_accessor import BaseAccessor


class RabbitAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.connection = None
        self.channel = None
        self.queue = None

    async def connect(self, app: "Application"):
        self.connection = await connect("amqp://guest:guest@localhost/")
        self.channel = await self.connection.channel()
        self.queue = await self.channel.declare_queue("main_queue")

    async def disconnect(self, app: "Application"):
        if self.connection:
            self.connection.close()

    async def send_to_queue(self, message: bytes):
        await self.channel.default_exchange.publish(
            Message(message),
            routing_key=self.queue.name,
        )
