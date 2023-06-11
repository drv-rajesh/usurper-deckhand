import os
import asyncio
import logging

import discord
from discord.ext import commands

token = os.environ["TOKEN"]
bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

async def main():
  await bot.load_extension("console")
  await bot.load_extension("reputation")

asyncio.run(main())
bot.run(token, log_handler=logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w"))
