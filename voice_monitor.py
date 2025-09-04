import os
import asyncio
import logging
from prometheus_client import start_http_server, Gauge
import discord

# Config from environment variables
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")  # Bot token
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))  # Server ID
VOICE_CHANNEL_ID = int(os.getenv("DISCORD_VOICE_CHANNEL_ID"))  # Voice channel ID
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 60))  # Check interval (sec)
PROM_PORT = int(os.getenv("PROM_PORT", 9100))  # Metrics port

# Prometheus metrics
voice_status = Gauge("discord_voice_connection", "Voice connection status (1=ok, 0=fail)")

# Logging configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("voice-monitor")

# Discord client
intents = discord.Intents.default()
intents.guilds = True
intents.voice_states = True
client = discord.Client(intents=intents)

async def check_voice():
    """Check voice channel connection."""
    await client.wait_until_ready()
    guild = client.get_guild(GUILD_ID)
    if not guild:
        logger.error("Guild not found!")
        return

    channel = guild.get_channel(VOICE_CHANNEL_ID)
    if not channel or not isinstance(channel, discord.VoiceChannel):
        logger.error("Voice channel not found!")
        return

    while not client.is_closed():
        try:
            # Connect to voice channel
            vc = await channel.connect(timeout=10, reconnect=False)
            await asyncio.sleep(3)  # Let connection stabilize

            if vc.is_connected():
                logger.info("✅ Successfully connected to voice")
                voice_status.set(1)
            else:
                logger.warning("⚠️ Failed to connect to voice")
                voice_status.set(0)

            await vc.disconnect(force=True)

        except Exception as e:
            logger.error(f"Connection error: {e}")
            voice_status.set(0)

        await asyncio.sleep(CHECK_INTERVAL)

@client.event
async def on_ready():
    logger.info(f"Started as {client.user} (id={client.user.id})")
    client.loop.create_task(check_voice())

if __name__ == "__main__":
    # Start Prometheus endpoint
    start_http_server(PROM_PORT)
    client.run(DISCORD_TOKEN)
