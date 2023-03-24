# Words game bot
A Telegram/VK bot that can run the word game in chat.

## What is it?

Words game bot is a bot for Telegram and for VK. It runs a game in chat, in which all players should propose words in turn, and each new word should start with the letter last word ends. I started working on it as a graduation project of a study course of the asynchronous python.

The bot is written on python and is using aiohttp library. it's asynchronous and can manage games running in multiple chats at once. The bot is divided into several services for stability. It uses Postgres for storing all data required in game, and RabbitMQ for messaging between services.

## Installation/Usage

It's my study project and I can't guarantee its working. Download the code base, edit the config files in bot folder and poller folder (bot ID to connect to your TG or VK bot), then use docker-compose to build and run the app.
