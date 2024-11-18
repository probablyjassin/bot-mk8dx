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
curl -O https://raw.githubusercontent.com/probablyjassin/bot-mk8dx/refs/heads/main/example.env
```

- comlpete the `example.env` with real values
- rename `example.env` to `.env`


```bash
docker compose up -d
```

That's it! The bot uses [docker watchtower](https://github.com/containrrr/watchtower) to automatically restart the bot when the docker image gets updated!



# Season 3 of MK8DX-Lounge on Yuzu Online!

<!-- Toggle one of these to your liking -->
<img width="1920" alt="MK8DX-Lounge Season 3 Summary" src="https://github.com/user-attachments/assets/35ab3a13-1696-41ff-9869-e1f5a0ceee40">
<!-- <img width="1920" alt="MK8DX-Lounge Season 3 Banner" src="https://github.com/user-attachments/assets/561c885e-aaa1-4130-a0c2-d0e9f46a8ccb"> -->


We're happy to present the next season of Lounge to you!
There is tons of new things we prepared for you all

### MMR reset
As with every new season, your MMR gets rolled back to some point.
You will start the new season at the starting MMR of the rank below you, while you can't drop lower than 2500MMR.
And of course, players below 2000MMR get reset back to that starting point!

Examples:
```diff
bruv:
- 8210MMR (Diamond Rank)
+ 5100MMR (Platinum Rank)

darling:
- 2097MMR (Silver Rank)
+ 2000MMR (Silver Rank)

woodlover:
- 1MMR (Wood Rank)
+ 2000MMR (Silver Rank)
```

### Full MMR History
We now store your entire history of mogis, not just the latest 30!
This gives you move insight into your developements.

### Teams is back!
Teams haven't been working for the past few weeks, but now we've brought them back, fully functional and better than ever!
This is because, we now have an algorithm that finds the most fair teams by player MMR!

### /status and /room
The /status command that used to just say whether or not a mogi is open or not, and how many players are in, got completely overhauled!
It's now more detailed with what is actually going on right now.

**And it now displays how many people are on the Yuzu Lounge server!** 

Together with this, there is also **/room** now, which lets you see the amount of players and the most played game on EU Main!

### Full Bot rewrite
The bot for playing mogis got a massive overhaul, both from the outside and the inside! 
I completely rewrote it to bring you tons of bugfixes and other improvements. 
We're calling it **Lounge8dx** now and touched up it's user profile.

The tables for MMR results and the leaderboard (new, sleek, modern colors)

### Better DC and waiting handling
We're now limiting how long people can take to join a started mogi (exceptions may apply) to improve the flow of the sessions.
DCs are now better documented as well, to target their reasons and help fix them!

### New Rank Icons
Thanks to Dalos we have new, fresh looking icons for Ranks, enjoy!

### For Mogi Managers:
Collecting points is way easier now!
Instead of up to 4 fragile modal windows, you now just feed the bot your tablestring you already used on Lorenzis Table Maker anyway!

**And coming soon:**
Ujuj is working on a visual reader for tables! When this is ready, this process will be even easier for you!

---

#### That's it! Now enjoy Season 3 of MK8DX-Lounge on Yuzu Online!
