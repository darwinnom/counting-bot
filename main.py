import discord
from discord.ext import commands

TOKEN = "BOT_TOKEN"
COUNTING_CHANNEL_ID = 123456789  # Replace with the ID of the counting channel

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

webhook_cache = {}

@bot.event
async def on_ready():
    print(f'✅ Logged in as {bot.user}')

async def get_webhook(channel):
    """Fetch or create a webhook in the given channel and cache it."""
    if channel.id in webhook_cache:
        return webhook_cache[channel.id]

    try:
        webhooks = await channel.webhooks()
        for webhook in webhooks:
            if webhook.name == "CountingBot":
                webhook_cache[channel.id] = webhook
                return webhook

        webhook = await channel.create_webhook(name="CountingBot")
        webhook_cache[channel.id] = webhook
        return webhook

    except discord.Forbidden:
        print("❌ Bot lacks permission to manage webhooks.")
    except discord.HTTPException as e:
        print(f"❌ Error creating/fetching webhook: {e}")

    return None

@bot.event
async def on_message(message):
    if message.author.bot:  
        return

    if message.channel.id == COUNTING_CHANNEL_ID:
        try:
            number = int(message.content)  
            await message.delete()  

            webhook = await get_webhook(message.channel)
            if not webhook:
                print("❌ Could not get webhook, skipping message.")
                return

            await webhook.send(
                content=str(number),
                username=message.author.display_name,
                avatar_url=message.author.display_avatar.url
            )

        except ValueError:
            await message.delete()  
        except discord.HTTPException as e:
            print(f"❌ Discord API Error: {e}")

bot.run(TOKEN)
