# MK8DX-Lounge Bot for [Yuzu Online](https://dsc.gg/yuzuonline)

![MK8DX-Lounge Bot GitHub Banner](https://github.com/mk8dx-yuzu/mk8dx-bot/assets/56404895/8aaf00d2-d093-4b9a-a5bc-946754b996d2)

## What does this bot do?

- let people register to the Leaderboard
- let them join Mario Kart events
- manage their gaming session
- collect their points
- calculate their new MMR
- store all this data in a mongodb database

## How do I set it up?

```bash
curl -O https://raw.githubusercontent.com/probablyjassin/bot-mk8dx/refs/heads/main/docker-compose.yml
```

- make sure the .env is present

```bash
docker compose up -d
```

That's it! The bot uses [docker watchtower](https://github.com/containrrr/watchtower) to automatically restart the bot when the docker image gets updated!
