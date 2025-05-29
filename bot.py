import discord
from discord.ext import commands
import requests
import os
from openai import OpenAI
from flask import Flask
from threading import Thread
from dotenv import load_dotenv
load_dotenv()


# Keep-alive web server
app = Flask('')

@app.route('/')
def home():
    print("Ping received from UptimeRobot")
    return "I'm alive!"

def run_web():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    Thread(target=run_web).start()

# Load environment variables (Replit Secrets auto-load)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

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
            model="gpt-4o-mini",  # or gpt-3.5-turbo if you prefer
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response.choices[0].message.content.strip()
        await ctx.send(answer[:2000])  # Discord limit
    except Exception as e:
        await ctx.send(f"Error: {e}")

# Start the keep-alive server
keep_alive()

# Start the Discord bot
token = os.getenv("DISCORD_BOT_TOKEN")
if not token:
    raise ValueError("DISCORD_BOT_TOKEN is not set in environment variables.")

bot.run(token)