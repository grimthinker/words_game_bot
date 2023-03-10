import asyncio
import json

import aiormq
from aio_pika import connect
from aio_pika.abc import AbstractIncomingMessage

from app.base.base_accessor import BaseAccessor
from app.web.utils import tg_make_update_from_raw, vk_make_update_from_raw


class RabbitAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.connection = None
        self.channel = None
        self.rabbit_queue = None
        self.workers = list()
        self.is_running = False
        self.async_queue = asyncio.Queue()
        self.handle_task = None

    async def connect(self, app: "Application"):
        self.is_running = True
        result = await self.make_conection()
        if result:
            self.channel = await self.connection.channel()
            await self.channel.set_qos(prefetch_count=10)
            self.rabbit_queue = await self.channel.declare_queue("main_queue")
            await self.rabbit_queue.consume(self.on_message, no_ack=False)
            for _ in range(10):
                self.workers.append(asyncio.create_task(self._worker()))

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
        self.is_running = False
        for worker in self.workers:
            await worker.cancel()
        if self.connection:
            await self.connection.close()

    async def on_message(self, message: AbstractIncomingMessage):
        raw_upd_json = message.body.decode("utf-8")
        raw_updates = json.loads(raw_upd_json)
        if "updates" in raw_updates:
            for raw_update in raw_updates["updates"]:
                if self.app.config.bot.api == "tg":
                    update = tg_make_update_from_raw(raw_update)
                else:
                    update = vk_make_update_from_raw(raw_update)
                await self.async_queue.put(update)
        await message.ack()

    async def _worker(self):
        while self.is_running:
            update = await self.async_queue.get()
            await self.app.store.bots_manager.handle_update(update)
