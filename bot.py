import discord
from discord.ext import commands
import requests
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Discord setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Bot is online as {bot.user}')

@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')

@bot.command()
async def card(ctx, *, card_name):
    url = f'https://api.scryfall.com/cards/named?fuzzy={card_name}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        name = data.get('name', 'Unknown')
        image_url = data.get('image_uris', {}).get('normal', '')
        await ctx.send(f"**{name}**\n{image_url}")
    else:
        await ctx.send("Card not found.")

@bot.command()
async def ask(ctx, *, prompt):
    """Send a prompt to OpenAI and return the response."""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",  # or "gpt-3.5-turbo"
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content.strip()
        await ctx.send(answer[:2000])  # Discord character limit

    except Exception as e:
        await ctx.send(f"Error: {e}")

bot.run(os.getenv("DISCORD_BOT_TOKEN"))
