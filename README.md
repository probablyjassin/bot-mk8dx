# MK8DX-Lounge Bot for [Yuzu Online](https://dsc.gg/yuzuonline)

![MK8DX-Lounge Bot GitHub Banner](https://github.com/mk8dx-yuzu/mk8dx-bot/assets/56404895/8aaf00d2-d093-4b9a-a5bc-946754b996d2)

# What does this bot do?

- let people register to the Leaderboard
- let them join Mario Kart events
- manage their gaming session
- collect their points
- calculate their new MMR
- store all this data in a mongodb database
- SO much more under the hood

## How do I set it up?

**Important: This is coded specifically for the Yuzu Online Discord server.**
**You won't be able to run it out of the box, since this is a tailored solution for our large community server.**
**I will try to abstract and generalize the codebase more over time.**

```bash
curl -O https://raw.githubusercontent.com/probablyjassin/bot-mk8dx/refs/heads/main/docker-compose.yml
curl -O https://raw.githubusercontent.com/probablyjassin/bot-mk8dx/refs/heads/main/example.env
```

- comlpete the `example.env` and `lounge.example.config` with real values
- rename `example.env` to `.env`
- rename `lounge.example.config` to `lounge.config`

```bash
docker compose up -d
```

That's it! Uncomment the [docker watchtower](https://github.com/containrrr/watchtower) section in the `docker-compose.yml` to automatically fetch updates to restart the bot when changes are detected!

# Season 5 of MK8DX-Lounge on Yuzu Online!

<img width="4000" height="2812" alt="Yuzu Online Lounge Season 5 Banner" src="https://github.com/user-attachments/assets/f0ab0af9-9e22-45ad-8e8c-c10fbfc13e7f" />

We're happy to present the brand new season of Lounge to you! There is many new things we prepared for you this time!

## MMR reset

We are bringing back the _significant_ resets from last season!
We used a method that **resets top rated players by a lot more** than lower rated ones.

In general:
**The further away you were from 2000, the more you got brought towards it!**

Examples:

```diff
bruv:
- 12000MMR (Master Rank)
+ 4935MMR (Gold Rank)

darling:
- 3000MMR (Silver Rank)
+ 2415MMR (Silver Rank)

woodlover:
- 1MMR (Wood Rank)
+ 1255MMR (Silver Rank)
```

## Statistics!

Changes from Season 4 onwards were all about statistics.
You've already seen tons of awesome new ways to see your history in our lounge added to the lounge website by Kevnkkm.
Now we are bringing some to the bot as well!

## Many Bot optimizations

The Lounge Bot has been steadily improving all the time. For this season we make lots of improvements to the general experience, like **getting rid of the unnecessary vote when you're starting with 7, 9 or 11 players**, and ma

---

#### That's it! Now enjoy Season 5 of MK8DX-Lounge on Yuzu Online!
