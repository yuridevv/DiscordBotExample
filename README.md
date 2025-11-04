# DiscordBotExample
A multifunctional Discord bot built with **discord.py**, featuring an XP system, fun commands, server info utilities, GIF integration, and even a simple turn-based combat system.

---

## ✨ Features

- 🧠 **XP System** — Earn and manage XP stored in an SQLite database  
- 🎮 **Combat System** — Challenge friends to simple turn-based duels  
- 🖼️ **GIF Search** — Pull random GIFs from Giphy using keywords  
- 🧹 **Moderation Tools** — Clear messages and monitor server activity  
- 👋 **Welcome Messages** — Greet new members automatically with a random GIF  
- 🧾 **User & Server Info** — Quick lookups for member or server details  

---

## 🛠️ Tech Stack

- [Python 3.10+](https://www.python.org/)
- [discord.py](https://discordpy.readthedocs.io/en/stable/)
- [SQLite3](https://www.sqlite.org/index.html)
- [aiohttp](https://docs.aiohttp.org/en/stable/)
- [Giphy API](https://developers.giphy.com/)

---

## 🚀 Setup & Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yuridevv/DiscordBotExample
   cd DiscordBotExample

2. **Install Requirements**
   use pip install
   
3. Create a .env file in the project root and add:
   ```bash
   DISCORD_BOT_TOKEN=your_discord_token_here
   GIPHY_API_KEY=your_giphy_api_key_here

4. Run the bot :)
   ```bash
     python bot.py


## Command Example
| Command                  | Description                        |
| ------------------------ | ---------------------------------- |
| `-ping`                  | Check the bot’s latency            |
| `-clock`                 | Get the current time               |
| `-userinfo [user]`       | Show info about a user             |
| `-serverinfo`            | Display server details             |
| `-gif [keyword]`         | Get a random GIF                   |
| `-addxp [amount] [user]` | Add XP to a user                   |
| `-combat [user]`         | Challenge another user to a fight  |
| `-attack`                | Attack your opponent during combat |
| `-clear [amount]`        | Delete a number of messages        |
| `-help`                  | Show all available commands        |


