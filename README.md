# ⏳ Time Capsule Discord Bot

This is a Discord bot that lets users bury/store a message and have it automatically sent back to them in a direct message (DM) after a delay.

## 🚀 Features

- `!save <time> <message>` — Save a message to be delivered to you later.
  - Time formats: `s` (seconds), `m` (minutes), `h` (hours), `d` (days)
  - Example: `!save 10s Hello future me!`
- Auto DMs you once the timer ends.
- Simple and private — everything is stored locally.

## 📦 Requirements

- Python 3.8+
- Discord bot token
- Dependencies (installed via pip):
  ```bash
  pip install -r requirements.txt
