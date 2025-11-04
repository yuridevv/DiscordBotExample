import discord
from discord.ext import commands
import datetime
import random
import aiohttp
import sqlite3
import os
import asyncio

# ==============================
# Discord Bot Configuration
# ==============================

# Define intents (required for accessing message content, members, etc.)
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True

# Initialize the bot client with a command prefix and disabled default help command
client = commands.Bot(command_prefix='-', help_command=None, intents=intents)

# ==============================
# SQLite Database Configuration
# ==============================

# Create or connect to a local SQLite database
db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "xp_system.db")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create a table to store user XP data if it doesn't already exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    xp INTEGER DEFAULT 0
)
''')

conn.commit()
conn.close()

# ==============================
# Active Combat System Tracker
# ==============================
active_combats = {}

# ==============================
# Giphy API Request Function
# ==============================

async def get_gif_url(query):
    """Fetches a GIF URL from the Giphy API based on a search query."""
    api_key = os.getenv("GIPHY_API_KEY")  # Load key from environment variable
    url = f'https://api.giphy.com/v1/gifs/search?api_key={api_key}&q={query}&limit=10&rating=g'

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                gifs = data.get('data', [])
                if gifs:
                    chosen = random.choice(gifs)
                    return chosen['images']['original']['url']
    return None

# ==============================
# XP System
# ==============================

def add_xp(user_id, xp_to_add):
    """Adds XP to a user in the database, or creates a new entry if missing."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT xp FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        
        if result:
            new_xp = result[0] + xp_to_add
            cursor.execute('UPDATE users SET xp = ? WHERE user_id = ?', (new_xp, user_id))
        else:
            cursor.execute('INSERT INTO users (user_id, xp) VALUES(?, ?)', (user_id, xp_to_add))

        conn.commit()

def get_xp(user_id):
    """Retrieves the current XP value of a user."""
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT xp FROM users WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        return result[0] if result else 0

# ==============================
# Bot Events
# ==============================

@client.event
async def on_ready():
    """Triggered when the bot successfully connects to Discord."""
    current_time = datetime.datetime.now().strftime("%H:%M")
    print(f"Bot connected as {client.user}")
    print(f"Bot online at {current_time}")

# ==============================
# Bot Commands
# ==============================

@client.command(help="Displays the bot's latency in milliseconds.")
async def ping(ctx):
    latency = client.latency * 1000
    await ctx.reply(f':ping_pong: Pong! **{latency:.2f}ms**')

@client.command(help="Shows the current system time.")
async def clock(ctx):
    current_time = datetime.datetime.now().strftime("%H:%M")
    await ctx.reply(f"It is **{current_time}** o'clock :)")

@client.command(help="Deletes a given number of recent messages (max 100).")
async def clear(ctx, number: int = None):
    if number is None or number <= 0:
        await ctx.reply("ERROR: Invalid number.")
        return
    elif number > 100:
        await ctx.reply("ERROR: Number cannot exceed 100.")
        return
    await ctx.channel.purge(limit=number + 1)
    await ctx.send(f"{number} messages cleared! {ctx.author.mention}", delete_after=20)

@client.command(help="Adds XP to a user manually.")
async def addxp(ctx, value: int, member: discord.Member = None):
    member = member or ctx.author
    add_xp(member.id, value)
    await ctx.reply(f"**{value}** XP added to **{member.name}**.")

@client.command(help="Displays information about a user.")
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title="User Information", color=discord.Color.random())
    if member.avatar:
        embed.set_thumbnail(url=member.avatar.url)
    embed.add_field(name="Name", value=member.name, inline=True)
    embed.add_field(name="User ID", value=member.id, inline=False)
    embed.add_field(name="Discord Account Created", value=member.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="Joined Server On", value=member.joined_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="Top Role", value=member.top_role.name, inline=False)
    embed.add_field(name="User XP", value=f"{get_xp(member.id)} XP", inline=True)
    await ctx.reply(embed=embed)

@client.command(help="Displays all available commands.")
async def help(ctx):
    embed = discord.Embed(title=f"{client.user}'s COMMANDS", color=discord.Color.random())
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)
    embed.add_field(name='"INFO" COMMAND', value="Get info about a command: `-info [command]`", inline=True)
    embed.add_field(name="General", value="-ping; -clock; -userinfo; -serverinfo", inline=False)
    embed.add_field(name="Fun", value="-gif", inline=False)
    embed.add_field(name="Testing", value="-fakejoin", inline=False)
    await ctx.reply(embed=embed)

@client.command(help="Displays information about a specific command.")
async def info(ctx, command: str = None):
    if not command:
        await ctx.reply("Please specify a command name.")
        return
    command_obj = client.get_command(command)
    if command_obj:
        description = command_obj.help or "No description available."
        await ctx.reply(f"**{command_obj.name}**: {description}")
    else:
        await ctx.reply(":x: Command not found.")

@client.command(help="Displays information about the server.")
async def serverinfo(ctx):
    online = len([m for m in ctx.guild.members if m.status in [discord.Status.online, discord.Status.do_not_disturb]])
    embed = discord.Embed(title=f'"{ctx.guild.name}" INFORMATION', color=discord.Color.random())
    if ctx.guild.icon:
        embed.set_thumbnail(url=ctx.guild.icon.url)
    embed.add_field(name="Date Created", value=ctx.guild.created_at.strftime("%d/%m/%Y"), inline=True)
    embed.add_field(name="Member Count", value=f"{ctx.guild.member_count} members ({online} online)", inline=True)
    embed.add_field(name="Server Owner", value=f"{ctx.guild.owner.name} ({ctx.guild.owner.status})", inline=False)
    await ctx.send(embed=embed)

@client.event
async def on_command(ctx):
    """Logs every executed command in the console."""
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"Command Used: {ctx.command.name}\nAuthor: {ctx.author}\nChannel: {ctx.channel.name}\nTime: {current_time}")
    print("___________________________________________________________________________")

# ==============================
# Welcome Message
# ==============================

async def welcome_message(member, channel):
    """Sends a welcome message and a random 'welcome' GIF when a user joins."""
    current_time = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"----> {member} joined {member.guild.name} at {current_time}")
    print("___________________________________________________________________________")
    await channel.send(f"**Welcome to the server, {member.mention}!** Make yourself comfortable. ☕")
    url = await get_gif_url("welcome")
    if url:
        await channel.send(url)

@client.event
async def on_member_join(member):
    """Triggers the welcome message when a new member joins."""
    channel = member.guild.system_channel or discord.utils.get(member.guild.text_channels, permissions__send_messages=True)
    if channel:
        await welcome_message(member, channel)

@client.command(help="Simulates a new member joining the server (for testing).")
async def fakejoin(ctx):
    await welcome_message(ctx.author, ctx.channel)

# ==============================
# Combat System
# ==============================

class Combat:
    """Handles a turn-based combat between two Discord users."""

    def __init__(self, playerOne, playerTwo):
        self.playerOne = playerOne
        self.playerTwo = playerTwo
        self.life = {playerOne: 20, playerTwo: 20}
        self.turn = playerOne
        self.active = True

    def change_turn(self):
        """Switches the turn between players."""
        self.turn = self.playerTwo if self.turn == self.playerOne else self.playerOne    

    def attack(self, attacker):
        """Performs an attack action."""
        if not self.active:
            return "Combat is over."
        if attacker != self.turn:
            return "It's not your turn."

        defender = self.playerTwo if attacker == self.playerOne else self.playerOne
        self.life[defender] -= 10 

        if self.life[defender] <= 0:
            self.active = False
            return f"{attacker} won the combat!"

        self.change_turn()
        return f"{attacker} attacked {defender}! Remaining HP: {self.life[defender]}"

@client.command(help="Starts a combat challenge against another user.")
async def combat(ctx, member: discord.Member = None):
    if not member:
        await ctx.reply("You must mention a user to challenge.")
        return
    if member == ctx.author:
        await ctx.reply("You cannot challenge yourself.")
        return

    msg = await ctx.send(f"{member.mention}, you were challenged by {ctx.author.mention}! React with ⚔️ to accept.")
    await msg.add_reaction("⚔️")

    def check(reaction, user):
        return (
            user == member and
            str(reaction.emoji) == "⚔️" and
            reaction.message.id == msg.id
        )

    try:
        await client.wait_for("reaction_add", timeout=60.0, check=check)
    except asyncio.TimeoutError:
        await ctx.send("The challenge expired.", delete_after=20)
        return

    combat_instance = Combat(ctx.author, member)
    active_combats[ctx.channel.id] = combat_instance
    await ctx.send(f"**COMBAT STARTED: {ctx.author.mention} ⚔️ {member.mention}!**")

@client.command(help="Performs an attack in an active combat.")
async def attack(ctx):
    combat = active_combats.get(ctx.channel.id)

    if not combat:
        await ctx.send("No active combat found in this channel.")
        return
    
    result = combat.attack(ctx.author)
    await ctx.send(result)

    if not combat.active:
        del active_combats[ctx.channel.id]

# ==============================
# Bot Token
# ==============================

# The bot token should be stored securely in an environment variable.
# Example:
# client.run(os.getenv("DISCORD_BOT_TOKEN"))

