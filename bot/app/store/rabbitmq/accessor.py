import asyncio
import json

from aio_pika import Message, connect
from aio_pika.abc import AbstractIncomingMessage

from app import asyncpool
from app.base.base_accessor import BaseAccessor
from app.store.bot.constants import API
from app.web.utils import tg_make_update_from_raw, vk_make_update_from_raw


class RabbitAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.connection = None
        self.channel = None
        self.rabbit_queue = None
        self.pool = None
        self.is_running = False
        self.async_queue = asyncio.Queue()
        self.handle_task = None

    async def connect(self, app: "Application"):
        self.is_running = True
        self.handle_task = asyncio.create_task(self.handle())
        self.connection = await connect("amqp://guest:guest@localhost/")
        self.channel = await self.connection.channel()
        await self.channel.set_qos(prefetch_count=10)
        self.rabbit_queue = await self.channel.declare_queue("main_queue")
        await self.rabbit_queue.consume(self.on_message, no_ack=False)


    async def disconnect(self, app: "Application"):
        self.is_running = False
        if self.handle_task:
            await self.handle_task
        if self.connection:
            self.connection.close()

    async def on_message(self, message: AbstractIncomingMessage):
        raw_upd_json = message.body.decode('utf-8')
        raw_updates = json.loads(raw_upd_json)
        if "updates" in raw_updates:
            for raw_update in raw_updates["updates"]:
                if API == "tg":
                    update = tg_make_update_from_raw(raw_update)
                else:
                    update = vk_make_update_from_raw(raw_update)
                await self.async_queue.put(update)
        await message.ack()


    async def handle(self):
        async with asyncpool.AsyncPool(
            loop=asyncio.get_running_loop(),
            num_workers=10,
            name="HandlersPool",
            logger=self.app.store.bots_manager.logger,
            worker_co=self.app.store.bots_manager.handle_update,
            max_task_time=300,
            log_every_n=10,
        ) as pool:
            while self.is_running:
                update = await self.async_queue.get()
                await pool.push(update)