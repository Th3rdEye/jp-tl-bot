import logging

from discord import Intents
from discord.ext import commands

from config import TOKEN
from discord_slash import SlashCommand

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.FileHandler('tl_bot_logs.log', 'w', 'utf-8')
handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
logger.addHandler(handler)

Bot = commands.Bot(command_prefix="\\", intents=Intents.default())
slash = SlashCommand(Bot, sync_commands=True)

Bot.load_extension("cogs.Translate")

Bot.run(TOKEN)
