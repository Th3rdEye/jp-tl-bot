from langdetect import detect
import discord, requests, os, logging, json

logging.basicConfig(filename="tl_bot_logs.log", encoding="utf-8", level=logging.DEBUG, format='%(asctime)s %(message)s')

TOKEN = "OTYyMDQ1MTAxODIyMDUwMzc0.YlB0Ug.X7y4yngsu-0V89abDaR9aBQ84xU"
client = discord.Client()
IDS = [
    962046744059846666, # Personal server TL channel
    759255638961422357 # Rice Anime Club Discord bot-commands
]

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
            logging.error(f"Status code {resp.status_code} : Translation of '{msg}' failed : {error_codes[resp.status_code]}")
        else:
            logging.error(f"Status code {resp.status_code} : Translation of '{msg}' failed : Internal Server Error")
    else:
        try:
            result_json = json.loads(resp.text)
            result = result_json["translations"][0]["text"]
            logging.info(f"Status code {resp.status_code} : SUCCESS! Translated '{msg}' from source lang {source_lang} into {target_lang} : {result}")
            return result
        except Exception as ex:
            logging.error(f"Status code {resp.status_code} : Translation of '{msg}' failed due to exception : {ex}")
    return None

@client.event
async def on_ready():
    logging.info("Bot is online!")

@client.event
async def on_message(msg):
    if msg.author == client.user:
        return
    
    if msg.channel.id in IDS:
        await msg.channel.send(translate(msg.content))

client.run(TOKEN)