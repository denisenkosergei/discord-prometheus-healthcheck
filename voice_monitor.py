import os
import asyncio
import discord
from prometheus_client import Gauge, start_http_server
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("voice-monitor")

DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))
VOICE_CHANNEL_ID = int(os.getenv("DISCORD_VOICE_CHANNEL_ID"))
CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 300))
PROM_PORT = int(os.getenv("PROM_PORT", 9100))

voice_status = Gauge("discord_voice_connection", "1=ok,0=fail", ["guild_id", "channel_id"])

intents = discord.Intents.default()
intents.guilds = True
client = discord.Client(intents=intents)

async def ensure_voice_connection():
    """Reconnect to the voice channel if disconnected."""
    guild = client.get_guild(GUILD_ID)
    if not guild:
        logger.error("Guild not found")
        return

    channel = guild.get_channel(VOICE_CHANNEL_ID)
    if not channel or channel.type != discord.ChannelType.voice:
        logger.error("Voice channel not found")
        return

    vc = guild.voice_client
    if vc and vc.is_connected():
        voice_status.labels(str(GUILD_ID), str(VOICE_CHANNEL_ID)).set(1)
        return
    
    try:
        if vc:
            await vc.disconnect(force=True)
        vc = await channel.connect(timeout=10, reconnect=False)
        await asyncio.sleep(2)
        if vc.is_connected():
            logger.info("✅ Voice connected")
            voice_status.labels(str(GUILD_ID), str(VOICE_CHANNEL_ID)).set(1)
        else:
            logger.warning("⚠️ Failed to connect")
            voice_status.labels(str(GUILD_ID), str(VOICE_CHANNEL_ID)).set(0)
    except Exception as e:
        logger.error(f"Error connecting to voice: {e}")
        voice_status.labels(str(GUILD_ID), str(VOICE_CHANNEL_ID)).set(0)

async def monitor_loop():
    await client.wait_until_ready()
    while not client.is_closed():
        await ensure_voice_connection()
        await asyncio.sleep(CHECK_INTERVAL)

@client.event
async def on_ready():
    logger.info(f"Started as {client.user} (id={client.user.id})")
    client.loop.create_task(monitor_loop())

if __name__ == "__main__":
    start_http_server(PROM_PORT)
    client.run(DISCORD_TOKEN)
