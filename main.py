from langdetect import detect
import discord, requests, os, logging, json
from discord import Client, Intents
from discord_slash import SlashCommand, SlashContext
from discord_slash.utils.manage_commands import create_option

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.FileHandler('tl_bot_logs.log', 'w', 'utf-8')
handler.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
logger.addHandler(handler)

TOKEN = os.environ["DISCORD_TL_BOT_TOKEN"]
IDS = [
    962046744059846666, # Personal server TL channel
    759255638961422357 # Rice Anime Club Discord bot-commands
]

client = Client(intents=Intents.default())
Bot = SlashCommand(client)

translate_url = "https://api-free.deepl.com/v2/translate"
AUTH_KEY = os.environ["DEEPL_API_KEY"]
error_codes = {
    400 : "Bad request. Please check error message and your parameters.",
    403 : "Authorization failed. Please supply a valid auth_key parameter.",
    404 : "The requested resource could not be found.",
    413 : "The request size exceeds the limit.",
    414 : "The request URL is too long. You can avoid this error by using a POST request instead of a GET request, and sending the parameters in the HTTP body.",
    429 : "Too many requests. Please wait and resend your request.",
    456 : "Quota exceeded. The character limit has been reached.",
    503 : "Resource currently unavailable. Try again later.",
    529 : "Too many requests. Please wait and resend your request."
}

def translate(msg : str) -> str:
    """ Translates a message into English if the message is in Japanese, and translates into Japanese if message is in English.

    Args:
        msg (str): The message to translate.

    Returns:
        str : The translated message if API call succeeds, otherwise None.
    """
    source_lang = detect(msg)
    target_lang = "EN-US" if source_lang == "ja" else "JA"
    params = {
        "auth_key" : AUTH_KEY,
        "text" : msg,
        "target_lang" : target_lang
    }
    resp = requests.post(translate_url, params=params)
    if resp.status_code != 200:
        if resp.status_code in error_codes:
            logger.error(f"Status code {resp.status_code} : Translation of '{msg}' failed : {error_codes[resp.status_code]}")
        else:
            logger.error(f"Status code {resp.status_code} : Translation of '{msg}' failed : Internal Server Error")
    else:
        try:
            result_json = json.loads(resp.text)
            result = result_json["translations"][0]["text"]
            logger.info(f"Status code {resp.status_code} : SUCCESS! Translated '{msg}' from source lang {source_lang} into {target_lang} : {result}")
            return result
        except Exception as ex:
            logger.error(f"Status code {resp.status_code} : Translation of '{msg}' failed due to exception : {ex}")
    return None

@Bot.slash(name="tl", description="Translate between EN and JP.",options=[
    create_option(
        name="text",
        description="The message to translate",
        option_type=3,
        required=True
    )
])
async def tl(ctx: SlashContext, input: str):
    msg = translate(" ".join(input))
    embed = discord.Embed(
        description = f"{msg}",
        colour = discord.Colour.from_rgb(255, 255, 255)
    )
    await ctx.send(embed=embed)

client.run(TOKEN)
