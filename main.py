import os
import discord
from discord.ext import commands, tasks
import aiosqlite
from datetime import datetime, timedelta
from keep_alive import keep_alive  # Import the keep_alive function

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
DB_PATH = "timecapsule.db"

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS capsules (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                message TEXT NOT NULL,
                send_time TIMESTAMP NOT NULL
            )
        """)
        await db.commit()
    check_capsules.start()

@bot.command()
async def save(ctx, time: str, *, message: str):
    time_multipliers = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
    try:
        amount = int(time[:-1])
        unit = time[-1]
        if unit not in time_multipliers:
            await ctx.send("❌ Invalid time unit! Use s, m, h, d.")
            return
        seconds = amount * time_multipliers[unit]
    except:
        await ctx.send("❌ Invalid time format! Use s, m, h, d (e.g., 10s, 5m, 2h, 1d).")
        return

    send_time = datetime.utcnow() + timedelta(seconds=seconds)

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT INTO capsules (user_id, message, send_time) VALUES (?, ?, ?)",
            (ctx.author.id, message, send_time)
        )
        await db.commit()

    await ctx.send(f"⏳ Your message will be sent back to you in {time}!")

@tasks.loop(seconds=10)
async def check_capsules():
    print("⏱️ Checking for due messages...")
    now = datetime.utcnow()
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "SELECT id, user_id, message FROM capsules WHERE send_time <= ?", (now,)
        )
        rows = await cursor.fetchall()
        for row in rows:
            capsule_id, user_id, message = row
            try:
                user = await bot.fetch_user(user_id)
                await user.send(f"📬 **Your Time Capsule Message:**\n\n{message}")
                print(f"✅ Sent DM to user {user_id}")
            except Exception as e:
                print(f"❌ Could not send DM to user {user_id}: {e}")
            await db.execute("DELETE FROM capsules WHERE id = ?", (capsule_id,))
        await db.commit()

keep_alive()  # Start the uptime server
bot.run(os.getenv("_DISCORD_TOKEN"))  # Run bot with token from Replit secrets
