# discord-prometheus-healthcheck
### ⚠️ Vibecode alert! ⚠️

This project helps to healthcheck network availability of Discord Voice functionality.
It's especially usefull for people in countries like Russia, where Discord banned by local laws. 

### How to build:
```
docker build -t discord-voice-monitor .
```

### Required environment variables

| Variable                  | Type      | Description                    |
| :------------------------ | :-------  | :----------------------------- |
| DISCORD_TOKEN             | string    | Token for your discord bot     |
| DISCORD_GUILD_ID          | int       | Server ID                      |
| DISCORD_VOICE_CHANNEL_ID  | int       | Voice Channel ID               |
| CHECK_INTERVAL            | int       | Frequency of requests          |
| PROM_PORT                 | int       | Port for Prometheus endpoint   |

### Run
```
docker run -d \
  --name discord-voice-monitor \
  -e DISCORD_TOKEN="Your_token" \
  -e DISCORD_GUILD_ID="Your_server_id" \
  -e DISCORD_VOICE_CHANNEL_ID="Your_voice_channel_id" \
  -e CHECK_INTERVAL=60 \
  -e PROM_PORT=9100 \
  -p 9100:9100 \
  discord-voice-monitor
```

### Or using docker-compose
```
version: "3"

services:
  discord-voice-monitor:
    image: discord-voice-monitor:latest
    container_name: discord-voice-monitor
    environment:
      - DISCORD_TOKEN=$DISCORD_TOKEN
      - DISCORD_GUILD_ID=1234567890
      - DISCORD_VOICE_CHANNEL_ID=1234567890
      - CHECK_INTERVAL=60
      - PROM_PORT=9100
    tty: true
    ports:
      - 9100:9100
    restart: unless-stopped
```
