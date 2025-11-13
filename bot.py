# bot.py — fixed version
import discord
from discord import app_commands
from discord.ext import commands, tasks
import asyncio
from typing import Optional
from flask import Flask
from threading import Thread
import random
import datetime
import os
import aiohttp
import json



OWNER_ID = os.getenv("1382858887786528803")
# ------------------ Flask Keep-Alive ------------------
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    # run Flask in a separate thread (daemon so it won't block shutdown)
    app.run(host='0.0.0.0', port=8080)

Thread(target=run_flask, daemon=True).start()

# ------------------ Bot Setup ------------------
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='/', intents=intents)

# ------------------ Helper Functions ------------------
WARN_FILE = "warns.json"

def load_warns():
    if not os.path.exists(WARN_FILE):
        with open(WARN_FILE, "w") as f:
            json.dump({}, f)
    with open(WARN_FILE, "r") as f:
        return json.load(f)

def save_warns(data):
    with open(WARN_FILE, "w") as f:
        json.dump(data, f, indent=4)


def has_guild_permissions(user, **perms):
    """
    Accepts either discord.Member or discord.User-like objects.
    Returns True if user has *all* specified permissions in their guild_permissions.
    """
    gp = getattr(user, "guild_permissions", None)
    if gp is None:
        return False
    return all(getattr(gp, name, False) == value for name, value in perms.items())

def check_hierarchy(interaction: discord.Interaction, target: discord.Member) -> Optional[str]:
    # Validate context
    if not interaction.guild:
        return "This command can only be used in a server."
    invoker = interaction.user
    guild = interaction.guild
    bot_member = guild.me  # Member representing the bot in this guild

    # Basic checks
    if target == invoker:
        return "You cannot perform this action on yourself."
    if bot_member and target == bot_member:
        return "I can't perform that action on myself."
    # Ensure invoker is a Member (should be in guild context)
    if isinstance(invoker, discord.Member):
        if target.top_role >= invoker.top_role and invoker != guild.owner:
            return "You can't moderate this user because their role is equal or higher than yours."
    # Check bot hierarchy: bot must be able to act on the target
    if bot_member:
        if target.top_role >= bot_member.top_role and guild.owner_id != bot_member.id:
            return "I can't moderate this user because their role is equal or higher than mine."
    return None

# ------------------ Fun Commands ------------------
#slash command /hello
@bot.tree.command(name="hello", description="Say hello to Helper bot")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Hello! I am Helper Bot, how are you?")
#slash command /joke
@bot.tree.command(name="joke", description="Tells you a random joke")
async def joke(interaction: discord.Interaction):
    jokes = [
        "What did one snowman say to the other snowman? It smells like carrots over here!",
        "What did 20 do when it was hungry? Twenty-eight.",
        "Why are mountains so funny? They’re hill areas.",
        "Why wasn’t the cactus invited to hang out with the mushrooms? He wasn’t a fungi.",
        "Why did the scarecrow win an award? Because he was outstanding in his field.",
        "Why did the picture go to jail? It was framed.",
        "How do you make holy water? You boil the hell out of it.",
        "What time did the guy go to the dentist? Tooth thirty."
    ]
    await interaction.response.send_message(random.choice(jokes))

#slash coomand /corndog
@bot.tree.command(name="corndog", description="Summons the mighty corndog")
async def corndog(interaction: discord.Interaction):
    funny_texts = [
        "🍢 Behold... the sacred corndog of chaos.",
        "When life gets tough, become the corndog.",
        "You summoned the corndog... now deal with the consequences.",
        "A wild corndog appears. It knows your search history."
    ]
    gif_url = "https://cdn.discordapp.com/attachments/1396315775362404383/1432069114511360112/bounce.gif"
    embed = discord.Embed(title="🌭 CORNDOG RITUAL INITIATED 🌭",
                          description=random.choice(funny_texts),
                          color=discord.Color.gold())
    embed.set_image(url=gif_url)
    await interaction.response.send_message(embed=embed)
    
#slash command /random number
@bot.tree.command(name="randomnumber", description="Picks a random number between 1-200")
async def randomnumber(interaction: discord.Interaction):
    num = random.randint(1, 200)
    await interaction.response.send_message(f"Your random number is: {num}")
    
#slash command /compliment
@bot.tree.command(name="compliment", description="Compliments you")
async def compliment(interaction: discord.Interaction):
    compliments = [
        "You’re awesome! 🌟",
        "Your smile lights up the room! 😊",
        "You’re a genius! 🧑‍💻",
        "**YOU**, yes **YOU**, are a very cool person!",
        "You’re super good at being cool!"
    ]
    await interaction.response.send_message(random.choice(compliments))

#slash command /ping
@bot.tree.command(name="ping", description="Check the bot's latency.")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    embed = discord.Embed(title="🏓 Pong! Bot is up and running",
                          description=f"Latency: **{latency}ms**",
                          color=discord.Color.gold())
    embed.set_footer(text="Helper Bot • Always here to help!")
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="flip", description="Flip a coin (Heads or Tails)")
async def flip(interaction: discord.Interaction):
    result = random.choice(["Heads", "Tails"])
    await interaction.response.send_message(f"🪙 You flipped **{result}**!")

#slash command /8ball
@bot.tree.command(name="8ball", description="Ask the magic 8 ball a question!")
@app_commands.describe(question="Your question for the 8 ball")
async def eight_ball(interaction: discord.Interaction, question: str):
    responses = [
        "It is certain.", "Without a doubt.", "Yes – definitely.", "You may rely on it.",
        "As I see it, yes.", "Most likely.", "Outlook good.", "Yes.", "Signs point to yes.",
        "Reply hazy, try again.", "Ask again later.", "Better not tell you now.",
        "Cannot predict now.", "Concentrate and ask again.", "Don’t count on it.",
        "My reply is no.", "Outlook not so good.", "Very doubtful."
    ]
    answer = random.choice(responses)
    await interaction.response.send_message(f"🎱 **Question:** {question}\n💬 **Answer:** {answer}")

#slash command /meme
@bot.tree.command(name="meme", description="Get a random meme from Reddit!")
async def meme(interaction: discord.Interaction):
    await interaction.response.defer()
    async with aiohttp.ClientSession() as session:
        async with session.get("https://meme-api.com/gimme") as response:
            if response.status == 200:
                data = await response.json()
                embed = discord.Embed(title=data.get("title", "meme"), color=discord.Color.random())
                embed.set_image(url=data.get("url"))
                embed.set_footer(text=f"From r/{data.get('subreddit','unknown')}")
                await interaction.followup.send(embed=embed)
            else:
                await interaction.followup.send("😢 Couldn't fetch a meme right now. Try again later!")


# slash command /giveawaystart 
@bot.tree.command(name="giveawaystart", description="Start a giveaway")
@app_commands.describe(duration="Duration in minutes", prize="Prize name", winners="Number of winners (default 1)")
async def giveaway_start(interaction: discord.Interaction, duration: int, prize: str, winners: int = 1):
    await interaction.response.defer()
    end_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=duration)


    embed = discord.Embed(
        title="🎉 Giveaway Started! 🎉",
        description=f"**Prize:** {prize}\n**Hosted by:** {interaction.user.mention}\n**Ends:** <t:{int(end_time.timestamp())}:R>\n\nClick 🎟️ to enter!",
        color=discord.Color.green()
    )

    view = GiveawayView(bot, prize, winners, end_time)
    message = await interaction.followup.send(embed=embed, view=view)

    # Store info on the message itself for easy reference
    view.message = message
    view.entries = []
    view.host = interaction.user

    # Automatically end the giveaway
    await asyncio.sleep(duration * 60)
    await end_giveaway(bot, message, prize, winners, view.entries)

# --- /giveawayend ---
@bot.tree.command(name="giveawayend", description="End a giveaway manually")
@app_commands.describe(message_id="Message ID of the giveaway to end")
async def giveaway_end(interaction: discord.Interaction, message_id: str):
    channel = interaction.channel
    try:
        message = await channel.fetch_message(int(message_id))
        for child in message.components[0].children:
            if isinstance(child, discord.ui.Button) and hasattr(child, "view"):
                view = child.view
                prize = getattr(view, "prize", "Unknown prize")
                winners = getattr(view, "winners", 1)
                entries = getattr(view, "entries", [])
                await end_giveaway(bot, message, prize, winners, entries)
                await interaction.response.send_message("✅ Giveaway ended manually!", ephemeral=True)
                return
        await interaction.response.send_message("❌ Could not find that giveaway or it has no entries.", ephemeral=True)
    except Exception as e:
        await interaction.response.send_message(f"❌ Error ending giveaway: {e}", ephemeral=True)

# --- Helper to end giveaway ---
async def end_giveaway(bot, message, prize, winners, entries):
    channel = message.channel
    if not entries:
        await channel.send(f"😢 No one entered the giveaway for **{prize}**.")
    else:
        winner_list = random.sample(entries, min(len(entries), winners))
        winners_mention = ", ".join([f"<@{u}>" for u in winner_list])
        await channel.send(f"🎉 Congratulations {winners_mention}! You won **{prize}**!")

# --- View for giveaway button ---
class GiveawayView(discord.ui.View):
    def __init__(self, bot, prize, winners, end_time):
        super().__init__(timeout=None)
        self.bot = bot
        self.prize = prize
        self.winners = winners
        self.end_time = end_time
        self.entries = []
        self.message = None
        self.host = None

    @discord.ui.button(label="🎟️ Enter", style=discord.ButtonStyle.blurple)
    async def enter(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.entries:
            await interaction.response.send_message("❌ You already entered!", ephemeral=True)
            return

        self.entries.append(interaction.user.id)
        await interaction.response.send_message("✅ You entered the giveaway!", ephemeral=True)


# ------------------ Poll Command ------------------
@bot.tree.command(name="poll", description="Create a timed poll with up to 5 options.")
@app_commands.describe(question="Poll question")
async def poll(interaction: discord.Interaction, question: str,
               option1: str, option2: str,
               option3: str = None, option4: str = None, option5: str = None,
               duration: int = 60):
    options = [opt for opt in [option1, option2, option3, option4, option5] if opt]
    emojis = ["🅰️", "🅱️", "🇨", "🇩", "🇪"]

    if len(options) < 2:
        return await interaction.response.send_message("❌ You must provide at least two options.", ephemeral=True)

    embed = discord.Embed(title="📊 Poll", description=question, color=discord.Color.blurple())
    embed.add_field(name="Options",
                    value="\n".join(f"{emojis[i]} {options[i]}" for i in range(len(options))),
                    inline=False)
    embed.set_footer(text=f"Poll ends in {duration} seconds!")
    await interaction.response.send_message(embed=embed)
    message = await interaction.original_response()

    for i in range(len(options)):
        await message.add_reaction(emojis[i])

    try:
        await asyncio.sleep(duration)
        message = await interaction.channel.fetch_message(message.id)
        results = []
        for i in range(len(options)):
            emoji = emojis[i]
            reaction = next((r for r in message.reactions if str(r.emoji) == emoji), None)
            count = reaction.count - 1 if reaction else 0
            results.append((options[i], count))
        highest = max(r[1] for r in results)
        winners = [r[0] for r in results if r[1] == highest]
        if highest == 0:
            result_text = "No votes were cast."
        elif len(winners) == 1:
            result_text = f"🏆 **{winners[0]}** wins with **{highest}** votes!"
        else:
            result_text = f"🤝 It's a tie between: {', '.join(winners)}"
        result_embed = discord.Embed(title="📊 Poll Ended", description=question, color=discord.Color.green())
        result_embed.add_field(name="Results",
                               value="\n".join(f"{emojis[i]} {options[i]} — **{results[i][1]} votes**" for i in range(len(options))),
                               inline=False)
        result_embed.add_field(name="Outcome", value=result_text, inline=False)
        await interaction.followup.send(embed=result_embed)
    except Exception as e:
        print(f"[Poll Error] {e}")

# ------------------ Moderation Commands ------------------

# KICK
@bot.tree.command(name="kick", description="Kick a member from the server")
@app_commands.describe(member="Member to kick", reason="Reason (optional)")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: Optional[str] = None):
    if not interaction.guild:
        return await interaction.response.send_message("Server only.", ephemeral=True)
    if not has_guild_permissions(interaction.user, kick_members=True):
        return await interaction.response.send_message("You need Kick Members.", ephemeral=True)
    if not has_guild_permissions(interaction.guild.me, kick_members=True):
        return await interaction.response.send_message("I need Kick Members.", ephemeral=True)
    bad = check_hierarchy(interaction, member)
    if bad:
        return await interaction.response.send_message(bad, ephemeral=True)
    try:
        await member.kick(reason=reason)
        await interaction.response.send_message(f"✅ {member.mention} kicked. Reason: {reason or 'None'}")
    except Exception as e:
        await interaction.response.send_message(f"Failed: {e}", ephemeral=True)

# BAN
@bot.tree.command(name="ban", description="Ban a member from the server")
@app_commands.describe(member="Member to ban", reason="Reason (optional)")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: Optional[str] = None):
    if not interaction.guild:
        return await interaction.response.send_message("Server only.", ephemeral=True)
    if not has_guild_permissions(interaction.user, ban_members=True):
        return await interaction.response.send_message("You need Ban Members.", ephemeral=True)
    if not has_guild_permissions(interaction.guild.me, ban_members=True):
        return await interaction.response.send_message("I need Ban Members.", ephemeral=True)
    bad = check_hierarchy(interaction, member)
    if bad:
        return await interaction.response.send_message(bad, ephemeral=True)
    try:
        await member.ban(reason=reason, delete_message_days=0)
        await interaction.response.send_message(f"✅ {member.mention} banned. Reason: {reason or 'None'}")
    except Exception as e:
        await interaction.response.send_message(f"Failed: {e}", ephemeral=True)

# UNBAN
@bot.tree.command(name="unban", description="Unban a user by ID")
@app_commands.describe(user_id="ID of the user to unban")
async def unban(interaction: discord.Interaction, user_id: int):
    if not interaction.guild:
        return await interaction.response.send_message("Server only.", ephemeral=True)
    if not has_guild_permissions(interaction.user, ban_members=True):
        return await interaction.response.send_message("You need Ban Members.", ephemeral=True)
    if not has_guild_permissions(interaction.guild.me, ban_members=True):
        return await interaction.response.send_message("I need Ban Members.", ephemeral=True)
    try:
        user = await bot.fetch_user(user_id)
        await interaction.guild.unban(user)
        await interaction.response.send_message(f"✅ Unbanned {user} ({user.id})")
    except Exception as e:
        await interaction.response.send_message(f"Failed: {e}", ephemeral=True)

# TIMEOUT
@bot.tree.command(name="timeout", description="Timeout a member for X minutes")
@app_commands.describe(member="Member", minutes="Duration in minutes", reason="Reason (optional)")
async def timeout(interaction: discord.Interaction, member: discord.Member, minutes: int = 10, reason: Optional[str] = None):
    if not interaction.guild:
        return await interaction.response.send_message("Server only.", ephemeral=True)
    if minutes < 1 or minutes > 40320:
        return await interaction.response.send_message("1-40320 minutes only.", ephemeral=True)
    if not has_guild_permissions(interaction.user, moderate_members=True):
        return await interaction.response.send_message("You need Moderate Members.", ephemeral=True)
    if not has_guild_permissions(interaction.guild.me, moderate_members=True):
        return await interaction.response.send_message("I need Moderate Members.", ephemeral=True)
    bad = check_hierarchy(interaction, member)
    if bad:
        return await interaction.response.send_message(bad, ephemeral=True)
    try:
        await member.edit(timeout=datetime.timedelta(minutes=minutes), reason=reason)
        await interaction.response.send_message(f"✅ {member.mention} timed out for {minutes} min. Reason: {reason or 'None'}")
    except Exception as e:
        await interaction.response.send_message(f"Failed: {e}", ephemeral=True)

# UNTIMEOUT
@bot.tree.command(name="untimeout", description="Remove timeout from a member")
@app_commands.describe(member="Member", reason="Reason")
async def untimeout(interaction: discord.Interaction, member: discord.Member, reason: Optional[str] = None):
    if not interaction.guild:
        return await interaction.response.send_message("Server only.", ephemeral=True)
    if not has_guild_permissions(interaction.user, moderate_members=True):
        return await interaction.response.send_message("You need Moderate Members.", ephemeral=True)
    if not has_guild_permissions(interaction.guild.me, moderate_members=True):
        return await interaction.response.send_message("I need Moderate Members.", ephemeral=True)
    bad = check_hierarchy(interaction, member)
    if bad:
        return await interaction.response.send_message(bad, ephemeral=True)
    try:
        await member.edit(timeout=None, reason=reason)
        await interaction.response.send_message(f"✅ Timeout removed from {member.mention}. Reason: {reason or 'None'}")
    except Exception as e:
        await interaction.response.send_message(f"Failed: {e}", ephemeral=True)

# PURGE
@bot.tree.command(name="purge", description="Bulk delete messages (1-100)")
@app_commands.describe(number="Number of messages")
async def purge(interaction: discord.Interaction, number: int):
    if not interaction.guild:
        return await interaction.response.send_message("Server only.", ephemeral=True)
    if number < 1 or number > 100:
        return await interaction.response.send_message("1-100 only.", ephemeral=True)
    if not has_guild_permissions(interaction.user, manage_messages=True):
        return await interaction.response.send_message("You need Manage Messages.", ephemeral=True)
    if not has_guild_permissions(interaction.guild.me, manage_messages=True):
        return await interaction.response.send_message("I need Manage Messages.", ephemeral=True)
    await interaction.response.defer(ephemeral=True)
    try:
        deleted = await interaction.channel.purge(limit=number)
        await interaction.followup.send(f"✅ Deleted {len(deleted)} messages.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"Failed: {e}", ephemeral=True)

# LOCK
@bot.tree.command(name="lock", description="Lock channel")
async def lock(interaction: discord.Interaction):
    if not interaction.guild:
        return await interaction.response.send_message("Server only.", ephemeral=True)
    if not has_guild_permissions(interaction.user, manage_channels=True):
        return await interaction.response.send_message("You need Manage Channels.", ephemeral=True)
    if not has_guild_permissions(interaction.guild.me, manage_channels=True):
        return await interaction.response.send_message("I need Manage Channels.", ephemeral=True)
    try:
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
        await interaction.response.send_message("🔒 Channel locked.")
    except Exception as e:
        await interaction.response.send_message(f"Failed: {e}", ephemeral=True)

# UNLOCK
@bot.tree.command(name="unlock", description="Unlock channel")
async def unlock(interaction: discord.Interaction):
    if not interaction.guild:
        return await interaction.response.send_message("Server only.", ephemeral=True)
    if not has_guild_permissions(interaction.user, manage_channels=True):
        return await interaction.response.send_message("You need Manage Channels.", ephemeral=True)
    if not has_guild_permissions(interaction.guild.me, manage_channels=True):
        return await interaction.response.send_message("I need Manage Channels.", ephemeral=True)
    try:
        await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=None)
        await interaction.response.send_message("🔓 Channel unlocked.")
    except Exception as e:
        await interaction.response.send_message(f"Failed: {e}", ephemeral=True)

# WARN
@bot.tree.command(name="warn", description="Warn a member (DM + record)")
@app_commands.describe(member="Member", reason="Reason")
async def warn(interaction: discord.Interaction, member: discord.Member, reason: Optional[str] = None):
    if not interaction.guild:
        return await interaction.response.send_message("Server only.", ephemeral=True)
    if not has_guild_permissions(interaction.user, kick_members=True):
        return await interaction.response.send_message("You need Kick/Ban permission.", ephemeral=True)
    bad = check_hierarchy(interaction, member)
    if bad:
        return await interaction.response.send_message(bad, ephemeral=True)

    data = load_warns()
    guild_id = str(interaction.guild.id)
    user_id = str(member.id)
    if guild_id not in data:
        data[guild_id] = {}
    if user_id not in data[guild_id]:
        data[guild_id][user_id] = []

    warn_info = {
        "reason": reason or "No reason provided",
        "by": str(interaction.user),
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

    data[guild_id][user_id].append(warn_info)
    save_warns(data)

    warns_list = data[guild_id][user_id]

    try:
        await member.send(
            f"⚠️ You were warned in **{interaction.guild.name}** by **{interaction.user}**.\n"
            f"Reason: {reason or 'None'}"
        )
    except:
        pass

    await interaction.response.send_message(
        f"✅ {member.mention} has been warned. Warning number {len(warns_list)}, 
        Reason: {reason or 'None'}"
    )



# warns
@bot.tree.command(name="warns", description="Check how many times a user has been warned")
@app_commands.describe(member="Member whose warnings you want to check")
async def warns(interaction: discord.Interaction, member: discord.Member):
    data = load_warns()
    guild_id = str(interaction.guild.id)
    user_id = str(member.id)

    if guild_id not in data or user_id not in data[guild_id]:
        return await interaction.response.send_message(f"{member.mention} has no warnings.", ephemeral=True)

    warns_list = data[guild_id][user_id]
    embed = discord.Embed(
        title=f"⚠️ Warnings for {member}",
        color=discord.Color.orange()
    )
    for i, warn in enumerate(warns_list, start=1):
        embed.add_field(
            name=f"#{i} - {warn['by']}",
            value=f"**Reason:** {warn['reason']}\n**Date:** {warn['timestamp']}",
            inline=False
        )
    embed.set_footer(text=f"Total warnings: {len(warns_list)}")
    await interaction.response.send_message(embed=embed)

# ------------------ Status ------------------
@tasks.loop(minutes=10)
async def update_status():
    guild_count = len(bot.guilds)
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.playing,
                                                       name=f"Helping {guild_count} servers"))

# ------------------ Events ------------------
@bot.event
async def on_ready():
    # start status loop only if not already running
    if not update_status.is_running():
        update_status.start()

    # Attempt to sync commands: prefer guild sync for instant updates if GUILD_ID provided
    try:
        GUILD_ID = os.getenv("GUILD_ID")
        if GUILD_ID:
            try:
                guild_id_int = int(GUILD_ID)
                guild = discord.Object(id=guild_id_int)
                await bot.tree.sync(guild=guild)
                print(f"✅ Logged in as {bot.user} | Commands synced to guild {guild_id_int}!")
            except ValueError:
                print(f"[on_ready] Invalid GUILD_ID value: {GUILD_ID} (must be int). Falling back to global sync.")
                await bot.tree.sync()
                print(f"✅ Logged in as {bot.user} | Commands globally synced!")
        else:
            await bot.tree.sync()
            print(f"✅ Logged in as {bot.user} | Commands globally synced!")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    await bot.process_commands(message)

# Bot Ready & Slash Command Sync

@bot.event
async def on_ready():
    # Sync all slash commands with Discord
    await bot.tree.sync()
    print(f"✅ Logged in as {bot.user} — Slash commands synced!")

    # Optional: print all registered slash commands for debug
    cmds = await bot.tree.fetch_commands()
    print("Registered slash commands:", [c.name for c in cmds])

# ------------------ Run Bot ------------------
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable not set. Set BOT_TOKEN before running.")

bot.run(TOKEN)
