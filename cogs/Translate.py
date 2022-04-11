import json

import requests
from discord import Embed, Colour
from langdetect import detect
from discord.ext.commands import Bot, Cog
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option

from config import AUTH_KEY, translate_url
from const import error_codes
from main import logger


class Translate(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    def _translate(self, msg: str) -> str:
        """ Translates a message into English if the message is in Japanese, and translates into Japanese if message is in English.

        Args:
            msg (str): The message to translate.

        Returns:
            str : The translated message if API call succeeds, otherwise None.
        """
        source_lang = detect(msg)
        target_lang = "EN-US" if source_lang == "ja" else "JA"
        params = {
            "auth_key": AUTH_KEY,
            "text": msg,
            "target_lang": target_lang
        }
        resp = requests.post(translate_url, params=params)
        if resp.status_code != 200:
            if resp.status_code in error_codes:
                logger.error(
                    f"Status code {resp.status_code} : Translation of '{msg}' failed : {error_codes[resp.status_code]}")
            else:
                logger.error(f"Status code {resp.status_code} : Translation of '{msg}' failed : Internal Server Error")
        else:
            try:
                result_json = json.loads(resp.text)
                result = result_json["translations"][0]["text"]
                logger.info(
                    f"Status code {resp.status_code} : SUCCESS! Translated '{msg}' from source lang {source_lang} into {target_lang} : {result}")
                return result
            except Exception as ex:
                logger.error(f"Status code {resp.status_code} : Translation of '{msg}' failed due to exception : {ex}")
        return None

    @cog_ext.cog_slash(name="translate", description="Translate between EN and JP.", options=[
        create_option(
            name="text",
            description="The message to translate",
            option_type=3,
            required=True
        )
    ])
    async def tl(self, ctx: SlashContext, text: str):
        msg = self._translate(" ".join(text))
        embed = Embed(
            description=f"{msg}",
            colour=Colour.from_rgb(255, 255, 255)
        )
        await ctx.send(embed=embed)


def setup(bot: Bot):
    bot.add_cog(Translate(bot))
