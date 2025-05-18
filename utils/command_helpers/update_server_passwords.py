import os, json
import requests
from discord.ext import commands

from config import PASSWORD_API_URL, PASSWORD_API_PASS, LOG_CHANNEL_ID


async def fetch_server_passwords(bot: commands.Bot) -> None:
    log_channel = await bot.fetch_channel(LOG_CHANNEL_ID)

    if not PASSWORD_API_URL and PASSWORD_API_PASS:
        return await log_channel.send(
            "🔣 `PASSWORD_API_URL` and/or `PASSWORD_API_PASS` missing - skipping password update"
        )

    try:
        response = requests.get(
            PASSWORD_API_URL,
            headers={"Signature-256": PASSWORD_API_PASS},
            data="lounge",
        )
        if response.status_code == 200:
            passwords_data = response.json()

            passwords_file_path = os.path.join("state", "passwords.json")
            os.makedirs(os.path.dirname(passwords_file_path), exist_ok=True)

            with open(passwords_file_path, "w", encoding="utf-8") as f:
                json.dump(passwords_data, f, indent=4, ensure_ascii=False)

            await log_channel.send(f"🔣 Successfully updated passwords file.")
        else:
            await log_channel.send(
                f"🔣 Failed to fetch passwords: {response.status_code}"
            )
    except Exception as e:
        await log_channel.send(f"🔣 Error updating passwords: {str(e)}")
