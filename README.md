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

# The 4th Season of MK8DX-Lounge on Yuzu Online!

<img width="4000" height="2812" alt="Yuzu Online Lounge Season 4 Banner" src="https://github.com/user-attachments/assets/f0ab0af9-9e22-45ad-8e8c-c10fbfc13e7f" />

We're happy to present the brand new season of Lounge to you! There is many new things we prepared for you this time!

## MMR reset

The MMR reset is a _significant_ one this time around!
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

## MINI MOGIS!

Some have been wishing for this **over a full year ago** in \#suggestions, and due to popular demand, we finally implemented it! Furthermore, MMR gains/losses are reduced to 60%

#### How it works:

When voting for the format, instead of picking FFA, 2v2, 3v3,... pick `Mini Mogi`!

Mini Mogis are always FFA, and they are **capped to 40 minutes of play time, or until you reach 6 races**! The Lounge Bot will also notify you in the mogi when the 40 minute threshold is reached.

## RANDOM Teams!

While voting for the format, you can now **press `Random Teams` before you pick**, to get **fully randomized teammates** if the vote ends in **2v2 or 3v3**!

## Full Format History

We now store which formats you played how often!

## Many Bot optimizations

The Lounge Bot has been steadily improving all the time. For this season we make lots of improvements to the general experience, like **getting rid of the unnecessary vote when you're starting with 7, 9 or 11 players**, and ma

## Ujuj's TABLE READER!

The Table Reader has finished development and works! Over the next few days, we will work hard on getting implemented right into the bot to automize tables for you!

## Automated Abuse Protection!

We implemented complex mechanics to flag and identify players who use VPNs, Proxies, and other kinds of Applications to try and use Alt-Accounts and such.

---

#### That's it! Now enjoy Season 4 of MK8DX-Lounge on Yuzu Online!
