import discord
from discord.ext import commands, tasks
import aiosqlite
import asyncio
from datetime import datetime, timedelta

intents = discord.Intents.default()
intents.message_content = True  # Make sure this is enabled in the Developer Portal too

bot = commands.Bot(command_prefix="!", intents=intents)

DB_PATH = "timecapsule.db"

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")
    # Create the database table if it doesn't exist
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
    """
    Save a message to be sent back after a certain time.
    Time format examples:
    10s (seconds), 5m (minutes), 2h (hours), 1d (days)
    """
    time_multipliers = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
    try:
        amount = int(time[:-1])
        unit = time[-1]
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
    print("⏱️ Checking for due messages...")  # Debug print
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

# 🔐 YOUR BOT TOKEN HERE (make sure to hide this in production!)
bot.run("Your_Bot_Token")

