import asyncio

import aiormq
from aio_pika import Message, connect

from app.base.base_accessor import BaseAccessor


class RabbitAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.connection = None
        self.channel = None
        self.queue = None

    async def connect(self, app: "Application"):
        result = await self.make_conection()
        if result:
            self.channel = await self.connection.channel()
            self.queue = await self.channel.declare_queue("main_queue")

    async def make_conection(self):
        host = self.app.config.rabbitmq.host
        port = self.app.config.rabbitmq.port
        for _ in range(3):
            try:
                self.connection = await connect(f"amqp://guest:guest@{host}:{port}/")
                return True
            except aiormq.exceptions.AMQPConnectionError:
                self.logger.info("rabbitmq connect call failed")
                await asyncio.sleep(5)
        return False

    async def disconnect(self, app: "Application"):
        if self.connection:
            await self.connection.close()

    async def send_to_queue(self, message: bytes):
        if self.channel:
            await self.channel.default_exchange.publish(
                Message(message),
                routing_key=self.queue.name,
            )
