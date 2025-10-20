# bot.py
import discord
from discord import app_commands
from discord.ext import commands
import datetime
from typing import Optional
from flask import Flask 
from threading import Thread
import random

app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

Thread(target=run).start()


app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # required for moderation actions

bot = commands.Bot(command_prefix='/', intents=intents)

@bot.tree.command(name="hello")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("hello i am helper bot")

@bot.tree.command(name="joke", description="Tells you a random joke")
async def joke(interaction: discord.Interaction):
    jokes = [
        "What did one snowman say to the other snowman? It smells like carrots over here!",
        "What did 20 do when it was hungry? Twenty-eight.",
        "Why are mountains so funny? They’re hill areas.",
        "Why wasn’t the cactus invited to hang out with the mushrooms? He wasn’t a fungi."
    ]
    await interaction.response.send_message(random.choice(jokes))

@bot.tree.command(name="corndog", description="summons the mighty corndog")
async def corndog(interaction: discord.Interaction):
    funny_texts = [
        "🍢 behold... the sacred corndog of chaos.",
        "when life gets tough, become the corndog.",
        "you summoned the corndog... now deal with the consequences.",
        "a wild corndog appears. it knows your search history."
    ]
    
    gif_url = "https://cdn.discordapp.com/attachments/1359070018922614905/1429858396554793134/nk-image-edit-bounce-zofk3wki.gif?ex=68f7aae7&is=68f65967&hm=9f88b2fef681f6e57ae7aaa81fb3df480beffce780a28fa75ede9c3b4b1053fe&"  # or your preferred GIF link

    embed = discord.Embed(
        title="🌭 CORNDOG RITUAL INITIATED 🌭",
        description=random.choice(funny_texts),
        color=discord.Color.gold()
    )
    embed.set_image(url=gif_url)
    
    await interaction.response.send_message(embed=embed)

# Slash Command /randomnumber
@bot.tree.command(name="randomnumber")
async def randomnumber(interaction: discord.Interaction):
    num = random.randint(1, 100)
    await interaction.response.send_message(f"Your random number is: {num}")

# Slash Command /compliment
@bot.tree.command(name="compliment")
async def compliment(interaction: discord.Interaction):
    compliments = [
        "You’re awesome! 🌟",
        "Your smile lights up the room! 😊",
        "You’re a genius! 🧑‍💻",
        "**YOU** yes, **YOU** are an || alpha sigma male ||"
    ]
    await interaction.response.send_message(random.choice(compliments))


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return


    # Don't forget to process slash commands!
    await bot.process_commands(message)

@bot.event
async def on_ready():
    print(f"Logged in as: {bot.user} (id: {bot.user.id})")
    # Sync slash commands to the guilds (global sync can take up to an hour;
    # for faster testing you can sync per-guild or run once)
    try:
        await bot.tree.sync()
        print("Slash commands synced.")
    except Exception as e:
        print("Failed to sync commands:", e)

# Utility checks
def has_guild_permissions(user: discord.Member, **perms):
    gp = user.guild_permissions
    return all(getattr(gp, name, False) == value for name, value in perms.items())

def check_hierarchy(interaction: discord.Interaction, target: discord.Member) -> Optional[str]:
    """Return error string if target cannot be moderated by the invoker/bot, else None."""
    invoker = interaction.user
    guild = interaction.guild
    bot_member = guild.me

    if target == invoker:
        return "You cannot perform this action on yourself."
    if target == bot_member:
        return "I can't perform that action on myself."
    # Invoker must have higher top role than target
    if isinstance(invoker, discord.Member) and target.top_role >= invoker.top_role and invoker != guild.owner:
        return "You can't moderate this user because their role is equal or higher than yours."
    # Bot must have higher top role than target
    if target.top_role >= bot_member.top_role and guild.owner_id != bot_member.id:
        return "I can't moderate this user because their role is equal or higher than mine."
    return None

# KICK
@bot.tree.command(name="kick", description="Kick a member from the server")
@app_commands.describe(member="Member to kick", reason="Reason for kick (optional)")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: Optional[str] = None):
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True); return
    if not has_guild_permissions(interaction.user, kick_members=True):
        await interaction.response.send_message("You need the Kick Members permission to use this.", ephemeral=True); return
    if not has_guild_permissions(interaction.guild.me, kick_members=True):
        await interaction.response.send_message("I don't have permission to kick members.", ephemeral=True); return

    bad = check_hierarchy(interaction, member)
    if bad:
        await interaction.response.send_message(bad, ephemeral=True); return

    try:
        await member.kick(reason=reason)
        await interaction.response.send_message(f"✅ {member.mention} has been kicked. Reason: {reason or 'No reason provided.'}")
    except Exception as e:
        await interaction.response.send_message(f"Failed to kick: {e}", ephemeral=True)

# BAN
@bot.tree.command(name="ban", description="Ban a member from the server")
@app_commands.describe(member="Member to ban", reason="Reason for ban (optional)")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: Optional[str] = None):
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True); return
    if not has_guild_permissions(interaction.user, ban_members=True):
        await interaction.response.send_message("You need the Ban Members permission to use this.", ephemeral=True); return
    if not has_guild_permissions(interaction.guild.me, ban_members=True):
        await interaction.response.send_message("I don't have permission to ban members.", ephemeral=True); return

    bad = check_hierarchy(interaction, member)
    if bad:
        await interaction.response.send_message(bad, ephemeral=True); return

    try:
        await member.ban(reason=reason, delete_message_days=0)
        await interaction.response.send_message(f"✅ {member.mention} has been banned. Reason: {reason or 'No reason provided.'}")
    except Exception as e:
        await interaction.response.send_message(f"Failed to ban: {e}", ephemeral=True)

# UNBAN (by user id)
@bot.tree.command(name="unban", description="Unban a user by ID")
@app_commands.describe(user_id="ID of the user to unban")
async def unban(interaction: discord.Interaction, user_id: int):
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True); return
    if not has_guild_permissions(interaction.user, ban_members=True):
        await interaction.response.send_message("You need the Ban Members permission to use this.", ephemeral=True); return
    if not has_guild_permissions(interaction.guild.me, ban_members=True):
        await interaction.response.send_message("I don't have permission to unban members.", ephemeral=True); return

    try:
        user = await bot.fetch_user(user_id)
        await interaction.guild.unban(user)
        await interaction.response.send_message(f"✅ Unbanned user {user} ({user.id}).")
    except Exception as e:
        await interaction.response.send_message(f"Failed to unban: {e}", ephemeral=True)

# TIMEOUT (moderate members)
@bot.tree.command(name="timeout", description="Timeout a member for X minutes")
@app_commands.describe(member="Member to timeout", minutes="Duration in minutes", reason="Reason (optional)")
async def timeout(interaction: discord.Interaction, member: discord.Member, minutes: int = 10, reason: Optional[str] = None):
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True); return
    if minutes < 1 or minutes > 28*24*60:
        await interaction.response.send_message("Duration must be between 1 minute and 40320 minutes (28 days).", ephemeral=True); return
    if not has_guild_permissions(interaction.user, moderate_members=True):
        await interaction.response.send_message("You need the Moderate Members permission to use this.", ephemeral=True); return
    if not has_guild_permissions(interaction.guild.me, moderate_members=True):
        await interaction.response.send_message("I don't have permission to timeout members.", ephemeral=True); return

    bad = check_hierarchy(interaction, member)
    if bad:
        await interaction.response.send_message(bad, ephemeral=True); return

    until = datetime.datetime.utcnow() + datetime.timedelta(minutes=minutes)
    try:
        await member.edit(timeout=until, reason=reason)
        await interaction.response.send_message(f"✅ {member.mention} timed out for {minutes} minute(s). Reason: {reason or 'No reason provided.'}")
    except Exception as e:
        await interaction.response.send_message(f"Failed to timeout: {e}", ephemeral=True)

# UNTIMEOUT
@bot.tree.command(name="untimeout", description="Remove timeout from a member")
@app_commands.describe(member="Member to remove timeout from", reason="Reason (optional)")
async def untimeout(interaction: discord.Interaction, member: discord.Member, reason: Optional[str] = None):
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True); return
    if not has_guild_permissions(interaction.user, moderate_members=True):
        await interaction.response.send_message("You need the Moderate Members permission to use this.", ephemeral=True); return
    if not has_guild_permissions(interaction.guild.me, moderate_members=True):
        await interaction.response.send_message("I don't have permission to modify timeouts.", ephemeral=True); return

    bad = check_hierarchy(interaction, member)
    if bad:
        await interaction.response.send_message(bad, ephemeral=True); return

    try:
        await member.edit(timeout=None, reason=reason)
        await interaction.response.send_message(f"✅ Removed timeout for {member.mention}.")
    except Exception as e:
        await interaction.response.send_message(f"Failed to remove timeout: {e}", ephemeral=True)

# PURGE (bulk delete)
@bot.tree.command(name="purge", description="Bulk delete messages from the channel (max 100)")
@app_commands.describe(number="Number of messages to delete (1-100)")
async def purge(interaction: discord.Interaction, number: int):
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True); return
    if number < 1 or number > 100:
        await interaction.response.send_message("You can delete between 1 and 100 messages.", ephemeral=True); return
    if not has_guild_permissions(interaction.user, manage_messages=True):
        await interaction.response.send_message("You need Manage Messages permission to use this.", ephemeral=True); return
    if not has_guild_permissions(interaction.guild.me, manage_messages=True):
        await interaction.response.send_message("I don't have Manage Messages permission.", ephemeral=True); return

    # Acknowledge the command first (to avoid "This interaction failed" if purge takes time)
    await interaction.response.defer(ephemeral=True)
    try:
        deleted = await interaction.channel.purge(limit=number)
        await interaction.followup.send(f"✅ Deleted {len(deleted)} messages.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"Failed to purge: {e}", ephemeral=True)

# LOCK / UNLOCK channel
@bot.tree.command(name="lock", description="Lock this channel (deny @everyone send messages)")
async def lock(interaction: discord.Interaction):
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True); return
    if not has_guild_permissions(interaction.user, manage_channels=True):
        await interaction.response.send_message("You need Manage Channels permission to use this.", ephemeral=True); return
    if not has_guild_permissions(interaction.guild.me, manage_channels=True):
        await interaction.response.send_message("I don't have Manage Channels permission.", ephemeral=True); return

    try:
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
        await interaction.response.send_message("🔒 Channel locked. @everyone cannot send messages.")
    except Exception as e:
        await interaction.response.send_message(f"Failed to lock channel: {e}", ephemeral=True)

@bot.tree.command(name="unlock", description="Unlock this channel")
async def unlock(interaction: discord.Interaction):
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True); return
    if not has_guild_permissions(interaction.user, manage_channels=True):
        await interaction.response.send_message("You need Manage Channels permission to use this.", ephemeral=True); return
    if not has_guild_permissions(interaction.guild.me, manage_channels=True):
        await interaction.response.send_message("I don't have Manage Channels permission.", ephemeral=True); return

    try:
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=None)
        await interaction.response.send_message("🔓 Channel unlocked.")
    except Exception as e:
        await interaction.response.send_message(f"Failed to unlock channel: {e}", ephemeral=True)

# WARN (DM the user)
@bot.tree.command(name="warn", description="Send a warning DM to a member")
@app_commands.describe(member="Member to warn", reason="Reason for the warning (optional)")
async def warn(interaction: discord.Interaction, member: discord.Member, reason: Optional[str] = None):
    if not interaction.guild:
        await interaction.response.send_message("This command can only be used in a server.", ephemeral=True); return
    if not has_guild_permissions(interaction.user, kick_members=True):
        await interaction.response.send_message("You need moderator permissions (Kick/Ban) to warn members.", ephemeral=True); return

    bad = check_hierarchy(interaction, member)
    if bad:
        await interaction.response.send_message(bad, ephemeral=True); return

    try:
        await member.send(f"You have been warned in **{interaction.guild.name}** by **{interaction.user}**.\nReason: {reason or 'No reason provided.'}")
        await interaction.response.send_message(f"✅ {member.mention} has been warned (DM sent).")
    except Exception as e:
        await interaction.response.send_message(f"Failed to DM the user: {e}", ephemeral=True)

# Generic error handler for app commands
@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    # You can expand specific error types here
    await interaction.response.send_message(f"Error: {error}", ephemeral=True)

# Run the bot
import os
TOKEN = os.getenv("BOT_TOKEN")
bot.run(TOKEN)
