# bot.py — fully fixed version
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
import time
from discord.ui import View, Button
await bot.load_extension("logs")



OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# ------------------ Flask Keep-Alive ------------------
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
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
    gp = getattr(user, "guild_permissions", None)
    if gp is None:
        return False
    return all(getattr(gp, name, False) == value for name, value in perms.items())


def check_hierarchy(interaction: discord.Interaction, target: discord.Member) -> Optional[str]:
    if not interaction.guild:
        return "This command can only be used in a server."

    invoker = interaction.user
    guild = interaction.guild
    bot_member = guild.me

    if target == invoker:
        return "You cannot perform this action on yourself."
    if bot_member and target == bot_member:
        return "I cannot do that to myself."

    if isinstance(invoker, discord.Member):
        if target.top_role >= invoker.top_role and invoker != guild.owner:
            return "You cannot moderate this user (their highest role is equal or higher)."

    if bot_member:
        if target.top_role >= bot_member.top_role:
            return "I cannot moderate this user (their role is higher than mine)."

    return None


# ------------------ Fun Commands ------------------
@bot.tree.command(name="hello", description="Say hello to Helper bot")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("Hello! I am Helper Bot, how are you?")

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

@bot.tree.command(name="corndog", description="Summons the mighty corndog")
async def corndog(interaction: discord.Interaction):
    funny_texts = [
        "🍢 Behold... the sacred corndog of chaos.",
        "When life gets tough, become the corndog.",
        "You summoned the corndog... now deal with the consequences.",
        "A wild corndog appears. It knows your search history."
    ]
    gif_url = "https://cdn.discordapp.com/attachments/1396315775362404383/1432069114511360112/bounce.gif"
    embed = discord.Embed(
        title="🌭 CORNDOG RITUAL INITIATED 🌭",
        description=random.choice(funny_texts),
        color=discord.Color.gold()
    )
    embed.set_image(url=gif_url)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="randomnumber", description="Picks a random number between 1-200")
async def randomnumber(interaction: discord.Interaction):
    await interaction.response.send_message(f"Your random number is: {random.randint(1, 200)}")

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

@bot.tree.command(name="ping", description="Check bot latency")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong! Bot is up and running!",
        description=f"Latency: **{latency}ms**",
        color=discord.Color.gold()
    )
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="flip", description="Flip a coin")
async def flip(interaction: discord.Interaction):
    await interaction.response.send_message(f"🪙 You flipped **{random.choice(['Heads','Tails'])}**!")

@bot.tree.command(name="8ball", description="Ask the 8 ball")
@app_commands.describe(question="Your question")
async def eight_ball(interaction: discord.Interaction, question: str):
    responses = [
        "It is certain.", "Without a doubt.", "Yes – definitely.",
        "Most likely.", "Outlook good.", "Reply hazy, try again.",
        "Ask again later.", "Better not tell you now.",
        "Don’t count on it.", "Outlook not so good.", "Very doubtful."
    ]
    await interaction.response.send_message(f"🎱 **Question:** {question}\n💬 **Answer:** {random.choice(responses)}")

# slash command /cute 
@bot.tree.command(name="cute", description="Get a random cute dog or cat picture!")
@app_commands.describe(animal="Choose dog or cat")
@app_commands.choices(animal=[
    app_commands.Choice(name="Dog", value="dog"),
    app_commands.Choice(name="Cat", value="cat")
])
async def cute(interaction: discord.Interaction, animal: app_commands.Choice[str]):
    await interaction.response.defer()

    async with aiohttp.ClientSession() as session:
        if animal.value == "dog":
            # Random dog API
            async with session.get("https://dog.ceo/api/breeds/image/random") as resp:
                data = await resp.json()
                pic = data["message"]
                title = "🐶 Cute Dog!"

        else:
            # Random cat API
            async with session.get("https://api.thecatapi.com/v1/images/search") as resp:
                data = await resp.json()
                pic = data[0]["url"]
                title = "🐱 Cute Cat!"

    embed = discord.Embed(title=title, color=discord.Color.random())
    embed.set_image(url=pic)

    await interaction.followup.send(embed=embed)

@bot.tree.command(name="avatar", description="Show a user's avatar")
async def avatar(interaction: discord.Interaction, member: discord.Member = None):
    member = member or interaction.user
    embed = discord.Embed(
        title=f"{member.name}'s Avatar",
        color=discord.Color.random()
    )
    embed.set_image(url=member.avatar)
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="cookie", description="Give someone a cookie 🍪")
async def cookie(interaction: discord.Interaction, member: discord.Member):
    await interaction.response.send_message(f"🍪 {interaction.user.mention} gave {member.mention} a **cookie!**")


# slash command /meme
@bot.tree.command(name="meme", description="Get a random meme from Reddit")
async def meme(interaction: discord.Interaction):
    await interaction.response.defer()
    async with aiohttp.ClientSession() as session:
        async with session.get("https://meme-api.com/gimme") as resp:
            if resp.status != 200:
                return await interaction.followup.send("Could not fetch a meme.")
            data = await resp.json()
            embed = discord.Embed(title=data["title"], color=discord.Color.random())
            embed.set_image(url=data["url"])
            embed.set_footer(text=f"From r/{data['subreddit']}")
            await interaction.followup.send(embed=embed)


# slash command /giveaway

class GiveawayView(discord.ui.View):
    def __init__(self, prize, winners):
        super().__init__(timeout=None)
        self.prize = prize
        self.winners = winners
        self.entries = []

    @discord.ui.button(label="🎟️ Enter", style=discord.ButtonStyle.blurple)
    async def enter(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id in self.entries:
            return await interaction.response.send_message("❌ You already entered!", ephemeral=True)

        self.entries.append(interaction.user.id)
        await interaction.response.send_message("✅ You entered the giveaway!", ephemeral=True)

async def end_giveaway(message, prize, winners, entries):
    channel = message.channel

    if not entries:
        return await channel.send(f"😢 No one entered the giveaway for **{prize}**.")

    winner_list = random.sample(entries, min(winners, len(entries)))
    mentions = ", ".join(f"<@{u}>" for u in winner_list)

    await channel.send(f"🎉 Congratulations {mentions}! You won **{prize}**!")


@bot.tree.command(name="giveawaystart", description="Start a giveaway")
@app_commands.describe(duration="Duration in minutes", prize="Prize", winners="Number of winners")
async def giveaway_start(interaction: discord.Interaction, duration: int, prize: str, winners: int = 1):
    await interaction.response.defer()

    end_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=duration)

    view = GiveawayView(prize, winners)

    embed = discord.Embed(
        title="🎉 Giveaway Started!",
        description=f"**Prize:** {prize}\n**Ends:** <t:{int(end_time.timestamp())}:R>\nClick 🎟️ to enter!",
        color=discord.Color.green()
    )

    msg = await interaction.followup.send(embed=embed, view=view)

    # Auto end
    asyncio.create_task(
        giveaway_auto_end(msg, prize, winners, duration, view)
    )

async def giveaway_auto_end(message, prize, winners, duration, view):
    await asyncio.sleep(duration * 60)
    await end_giveaway(message, prize, winners, view.entries)


@bot.tree.command(name="giveawayend", description="End giveaway early")
@app_commands.describe(message_id="ID of the giveaway message")
async def giveaway_end(interaction: discord.Interaction, message_id: str):
    try:
        msg = await interaction.channel.fetch_message(int(message_id))
    except Exception:
        return await interaction.response.send_message("Invalid message ID.", ephemeral=True)

    if not msg.components:
        return await interaction.response.send_message("That message has no giveaway button.", ephemeral=True)

    view = msg.components[0].children[0].view

    await end_giveaway(msg, view.prize, view.winners, view.entries)
    await interaction.response.send_message("Giveaway ended!", ephemeral=True)


# ------------------ POLL ------------------
@bot.tree.command(name="poll", description="Create a poll with up to 5 options")
@app_commands.describe(question="Poll question")
async def poll(interaction: discord.Interaction, question: str,
               option1: str, option2: str, option3: str = None,
               option4: str = None, option5: str = None,
               duration: int = 60):

    options = [o for o in [option1, option2, option3, option4, option5] if o]
    emojis = ["🅰️", "🅱️", "🇨", "🇩", "🇪"]

    if len(options) < 2:
        return await interaction.response.send_message("Need at least 2 options.", ephemeral=True)

    embed = discord.Embed(
        title="📊 Poll",
        description=question,
        color=discord.Color.blurple()
    )
    embed.add_field(
        name="Options",
        value="\n".join(f"{emojis[i]} {options[i]}" for i in range(len(options))),
        inline=False
    )
    embed.set_footer(text=f"Poll ends in {duration} seconds")

    await interaction.response.send_message(embed=embed)
    msg = await interaction.original_response()

    for i in range(len(options)):
        await msg.add_reaction(emojis[i])

    await asyncio.sleep(duration)

    msg = await interaction.channel.fetch_message(msg.id)
    results = []

    for i in range(len(options)):
        emoji = emojis[i]
        reaction = discord.utils.get(msg.reactions, emoji=emoji)
        count = reaction.count - 1 if reaction else 0
        results.append((options[i], count))

    highest = max(c for _, c in results)
    winners = [opt for opt, c in results if c == highest and highest != 0]

    if highest == 0:
        result_text = "No votes."
    elif len(winners) == 1:
        result_text = f"🏆 **{winners[0]}** wins with **{highest}** votes!"
    else:
        result_text = "Tie: " + ", ".join(winners)

    result_embed = discord.Embed(
        title="📊 Poll Ended",
        description=question,
        color=discord.Color.green()
    )
    result_embed.add_field(
        name="Results",
        value="\n".join(f"{emojis[i]} {options[i]} — **{results[i][1]} votes**"
                        for i in range(len(options))),
        inline=False
    )
    result_embed.add_field(name="Outcome", value=result_text, inline=False)

    await interaction.followup.send(embed=result_embed)


from discord.ui import View, Button

# ------------------ Help Command (Auto-Updating + Buttons) ------------------
@bot.tree.command(name="help", description="Show the help menu with all commands.")
async def help_command(interaction: discord.Interaction):

    # Create the embed
    embed = discord.Embed(
        title="📘 Help Menu",
        description="Here’s a list of all my available commands!",
        color=discord.Color.blue()
    )

    # Auto-detect commands
    fun_cmds = []
    utility_cmds = []
    moderation_cmds = []

    for cmd in bot.tree.get_commands():
        # Organize by name — you can adjust categories however you want
        if cmd.name in ["hello", "joke", "corndog", "randomnumber", "compliment", "ping", "flip", "8ball", "cute"]:
            fun_cmds.append(f"`/{cmd.name}`")

        elif cmd.name in ["warn", "clearwarnings", "giverole", "removerole"]:
            moderation_cmds.append(f"`/{cmd.name}`")

        else:
            utility_cmds.append(f"`/{cmd.name}`")

    # Add fields
    if fun_cmds:
        embed.add_field(name="🎉 Fun Commands", value="\n".join(fun_cmds), inline=False)

    if moderation_cmds:
        embed.add_field(name="🔧 Moderation Commands", value="\n".join(moderation_cmds), inline=False)

    if utility_cmds:
        embed.add_field(name="🛠 Utility Commands", value="\n".join(utility_cmds), inline=False)

    embed.set_footer(text="Thanks for using Helper Bot! 💙")

    # Buttons
    view = View()

    view.add_item(Button(
        label="Support Server",
        url="https://discord.gg/7mSV6kENz3"
    ))

    view.add_item(Button(
        label="Terms of Service",
        url="https://helper-bot-tos.carrd.co/"
    ))

    view.add_item(Button(
        label="Privacy Policy",
        url="https://helper-bot-privacy-policy.carrd.co/"
    ))

    await interaction.response.send_message(embed=embed, view=view)


# ------------------ User Info Command ------------------
@bot.tree.command(name="userinfo", description="Shows information about a user.")
@app_commands.describe(member="The user you want info about")
async def userinfo(interaction: discord.Interaction, member: discord.Member = None):

    member = member or interaction.user  # Default to command user

    embed = discord.Embed(
        title=f"👤 User Info — {member.name}",
        color=discord.Color.blurple()
    )

    embed.set_thumbnail(url=member.display_avatar.url)

    embed.add_field(name="📝 Username", value=str(member), inline=True)
    embed.add_field(name="🆔 User ID", value=str(member.id), inline=True)
    embed.add_field(name="🤖 Bot?", value="Yes" if member.bot else "No", inline=True)

    embed.add_field(
        name="📅 Account Created",
        value=member.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        inline=False
    )

    embed.add_field(
        name="📥 Joined Server",
        value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S") if member.joined_at else "Unavailable",
        inline=False
    )

    # Roles (except @everyone)
    roles = [role.mention for role in member.roles if role.name != "@everyone"]
    embed.add_field(
        name="🎭 Roles",
        value=", ".join(roles) if roles else "No Roles",
        inline=False
    )

    embed.set_footer(text="Helper Bot — User Information")

    await interaction.response.send_message(embed=embed)


# ------------------ Robust Server Info Command ------------------
@bot.tree.command(name="serverinfo", description="Shows information about the server.")
async def serverinfo(interaction: discord.Interaction):
    guild = interaction.guild
    if not guild:
        return await interaction.response.send_message("This command can only be used in a server.", ephemeral=True)

    try:
        # Owner (try cached first, then API fetch)
        owner = guild.owner
        if owner is None:
            try:
                owner = await guild.fetch_member(guild.owner_id)
            except Exception:
                try:
                    owner = await bot.fetch_user(guild.owner_id)
                except Exception:
                    owner = None

        # Basic counts
        member_count = guild.member_count or sum(1 for _ in guild.members)
        text_count = len(guild.text_channels)
        voice_count = len(guild.voice_channels)
        category_count = len(guild.categories)
        emoji_count = len(guild.emojis)
        boost_count = getattr(guild, "premium_subscription_count", 0)
        boost_tier = getattr(guild, "premium_tier", 0)

        # Roles: exclude @everyone, show a limited preview to avoid embed overflow
        roles = [r for r in guild.roles if r != guild.default_role]
        roles = sorted(roles, key=lambda r: r.position, reverse=True)  # highest-first
        max_roles_to_show = 25
        shown_roles = roles[:max_roles_to_show]
        roles_display = ", ".join(r.mention for r in shown_roles) if shown_roles else "No Roles"
        if len(roles) > max_roles_to_show:
            roles_display += f", and {len(roles) - max_roles_to_show} more..."
        # ensure field length < 1000 chars (safe margin)
        if len(roles_display) > 900:
            roles_display = roles_display[:900].rsplit(",", 1)[0] + " ..."

        # Build embed
        embed = discord.Embed(
            title=f"📂 Server Info — {guild.name}",
            color=discord.Color.blurple()
        )

        if guild.icon:
            try:
                embed.set_thumbnail(url=guild.icon.url)
            except Exception:
                pass

        embed.add_field(name="🆔 Server ID", value=str(guild.id), inline=True)
        embed.add_field(name="👑 Owner", value=str(owner) if owner else "Unavailable", inline=True)
        embed.add_field(name="🌎 Members", value=str(member_count), inline=True)

        embed.add_field(name="🚀 Boosts", value=str(boost_count), inline=True)
        embed.add_field(name="💎 Boost Level", value=str(boost_tier), inline=True)

        embed.add_field(
            name="📁 Channels",
            value=f"Text: {text_count}\nVoice: {voice_count}\nCategories: {category_count}",
            inline=False
        )

        embed.add_field(name="🎭 Roles", value=roles_display, inline=False)

        embed.add_field(name="😊 Emojis", value=str(emoji_count), inline=True)

        embed.add_field(
            name="📅 Created On",
            value=guild.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            inline=False
        )

        embed.set_footer(text="Helper Bot — Server Information")

        await interaction.response.send_message(embed=embed)

    except discord.HTTPException as http_err:
        # Likely an embed size / permissions / rate limit problem — send minimal fallback
        try:
            fallback = (
                f"**{guild.name}** — basic info\n"
                f"ID: {guild.id}\n"
                f"Members: {guild.member_count}\n"
                f"Owner: {str(guild.owner) if getattr(guild, 'owner', None) else 'Unavailable'}\n"
                f"Created: {guild.created_at.strftime('%Y-%m-%d')}"
            )
            await interaction.response.send_message(fallback, ephemeral=True)
        except Exception:
            await interaction.response.send_message("Could not fetch server info due to an error.", ephemeral=True)
    except Exception as e:
        # Generic catchall (log or print if you want)
        print(f"[serverinfo error] {e}")
        await interaction.response.send_message("An unexpected error occurred while fetching server info.", ephemeral=True)


# ------------------ Moderation Commands ------------------
# (i fixed it all angel              )

@bot.tree.command(name="kick", description="Kick a member")
async def kick(interaction: discord.Interaction, member: discord.Member, reason: Optional[str] = None):
    if not has_guild_permissions(interaction.user, kick_members=True):
        return await interaction.response.send_message("Missing permission.", ephemeral=True)

    bad = check_hierarchy(interaction, member)
    if bad:
        return await interaction.response.send_message(bad, ephemeral=True)

    try:
        await member.kick(reason=reason)
        await interaction.response.send_message(f"✅ {member.mention} kicked.")
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)

@bot.tree.command(name="ban", description="Ban a member")
async def ban(interaction: discord.Interaction, member: discord.Member, reason: Optional[str] = None):
    if not has_guild_permissions(interaction.user, ban_members=True):
        return await interaction.response.send_message("Missing permission.", ephemeral=True)

    bad = check_hierarchy(interaction, member)
    if bad:
        return await interaction.response.send_message(bad, ephemeral=True)

    try:
        await member.ban(reason=reason)
        await interaction.response.send_message(f"✅ {member.mention} banned.")
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)

@bot.tree.command(name="unban", description="Unban a user ID")
async def unban(interaction: discord.Interaction, user_id: int):
    if not has_guild_permissions(interaction.user, ban_members=True):
        return await interaction.response.send_message("Missing permission.", ephemeral=True)

    try:
        user = await bot.fetch_user(user_id)
        await interaction.guild.unban(user)
        await interaction.response.send_message(f"Unbanned {user}.")
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)

@bot.tree.command(name="timeout", description="Timeout a member")
async def timeout(interaction: discord.Interaction, member: discord.Member, minutes: int, reason: Optional[str] = None):
    if not has_guild_permissions(interaction.user, moderate_members=True):
        return await interaction.response.send_message("Missing permission.", ephemeral=True)

    if minutes < 1:
        return await interaction.response.send_message("Minutes must be 1+.", ephemeral=True)

    bad = check_hierarchy(interaction, member)
    if bad:
        return await interaction.response.send_message(bad, ephemeral=True)

    try:
        await member.edit(timeout=datetime.timedelta(minutes=minutes))
        await interaction.response.send_message(f"Timed out {member.mention} for {minutes} minutes.")
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)

@bot.tree.command(name="untimeout", description="Remove timeout")
async def untimeout(interaction: discord.Interaction, member: discord.Member):
    if not has_guild_permissions(interaction.user, moderate_members=True):
        return await interaction.response.send_message("Missing permission.", ephemeral=True)

    try:
        await member.edit(timeout=None)
        await interaction.response.send_message(f"Removed timeout from {member.mention}.")
    except Exception as e:
        await interaction.response.send_message(f"Error: {e}", ephemeral=True)

@bot.tree.command(name="purge", description="Delete messages")
async def purge(interaction: discord.Interaction, number: int):
    if not has_guild_permissions(interaction.user, manage_messages=True):
        return await interaction.response.send_message("Missing permission.", ephemeral=True)

    if number < 1 or number > 100:
        return await interaction.response.send_message("Enter 1-100.", ephemeral=True)

    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=number)
    await interaction.followup.send(f"Deleted {len(deleted)} messages.", ephemeral=True)

@bot.tree.command(name="lock", description="Lock channel")
async def lock(interaction: discord.Interaction):
    if not has_guild_permissions(interaction.user, manage_channels=True):
        return await interaction.response.send_message("Missing permission.", ephemeral=True)

    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
    await interaction.response.send_message("🔒 Channel locked.")

@bot.tree.command(name="unlock", description="Unlock channel")
async def unlock(interaction: discord.Interaction):
    if not has_guild_permissions(interaction.user, manage_channels=True):
        return await interaction.response.send_message("Missing permission.", ephemeral=True)

    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=None)
    await interaction.response.send_message("🔓 Channel unlocked.")


# ------------------ WARN SYSTEM ------------------
@bot.tree.command(name="warn", description="Warn a member")
async def warn(interaction: discord.Interaction, member: discord.Member, reason: Optional[str] = None):
    if not has_guild_permissions(interaction.user, kick_members=True):
        return await interaction.response.send_message("Missing permission.", ephemeral=True)

    bad = check_hierarchy(interaction, member)
    if bad:
        return await interaction.response.send_message(bad, ephemeral=True)

    data = load_warns()
    guild_id = str(interaction.guild.id)
    uid = str(member.id)

    if guild_id not in data:
        data[guild_id] = {}
    if uid not in data[guild_id]:
        data[guild_id][uid] = []

    warn_info = {
        "reason": reason or "No reason",
        "by": str(interaction.user),
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

    data[guild_id][uid].append(warn_info)
    save_warns(data)

    await interaction.response.send_message(
        f"⚠️ Warned {member.mention}. Total warnings: {len(data[guild_id][uid])}"
    )

# CLEAR ALL WARNS
@bot.tree.command(name="clearwarns", description="Clear all warnings for a member")
@app_commands.describe(member="Member whose warnings you want to clear")
async def clearwarns(interaction: discord.Interaction, member: discord.Member):

    if not has_guild_permissions(interaction.user, kick_members=True):
        return await interaction.response.send_message("Missing permission.", ephemeral=True)

    data = load_warns()
    guild_id = str(interaction.guild.id)
    uid = str(member.id)

    if guild_id in data and uid in data[guild_id]:
        data[guild_id][uid] = []
        save_warns(data)
        return await interaction.response.send_message(
            f"🗑️ Cleared all warnings for {member.mention}"
        )

    await interaction.response.send_message(
        f"{member.mention} has no warnings.", ephemeral=True
    )



@bot.tree.command(name="delwarn", description="Delete a single warning by number")
@app_commands.describe(member="Member", warn_number="Warning number to delete")
async def delwarn(interaction: discord.Interaction, member: discord.Member, warn_number: int):

    if not has_guild_permissions(interaction.user, kick_members=True):
        return await interaction.response.send_message("Missing permission.", ephemeral=True)

    data = load_warns()
    guild_id = str(interaction.guild.id)
    uid = str(member.id)

    if guild_id not in data or uid not in data[guild_id]:
        return await interaction.response.send_message(
            "This user has no warnings.", ephemeral=True
        )

    warns_list = data[guild_id][uid]

    if warn_number < 1 or warn_number > len(warns_list):
        return await interaction.response.send_message(
            "Invalid warning number.", ephemeral=True
        )

    removed = warns_list.pop(warn_number - 1)
    save_warns(data)

    await interaction.response.send_message(
        f"🗑️ Removed warning #{warn_number} from {member.mention}\n"
        f"**Removed reason:** {removed['reason']}"
    )


@bot.tree.command(name="warns", description="Check a user's warnings")
async def warns(interaction: discord.Interaction, member: discord.Member):
    data = load_warns()
    guild_id = str(interaction.guild.id)
    uid = str(member.id)

    if guild_id not in data or uid not in data[guild_id]:
        return await interaction.response.send_message("This user has no warnings.", ephemeral=True)

    warns_list = data[guild_id][uid]

    embed = discord.Embed(
        title=f"Warnings for {member}",
        color=discord.Color.orange()
    )

    for i, w in enumerate(warns_list, 1):
        embed.add_field(
            name=f"#{i} — by {w['by']}",
            value=f"Reason: {w['reason']}\nDate: {w['timestamp']}",
            inline=False
        )

    embed.set_footer(text=f"Total warnings: {len(warns_list)}")
    await interaction.response.send_message(embed=embed)

# ========== MESSAGE LOGGING SYSTEM (FULL COG) ==========
import discord
from discord.ext import commands
from discord import app_commands
import json
import os


# JSON load/save helpers
def load_logs():
    if not os.path.exists("log_config.json"):
        with open("log_config.json", "w") as f:
            json.dump({}, f)
    with open("log_config.json", "r") as f:
        return json.load(f)


def save_logs(data):
    with open("log_config.json", "w") as f:
        json.dump(data, f, indent=4)


class Logs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.logs = load_logs()  # Load saved log channels


    # ------------------ SET LOG CHANNEL ------------------
    @app_commands.command(
        name="set_message_log_channel",
        description="Set the channel used for message edit/delete logs."
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def set_message_log_channel(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel
    ):
        guild_id = str(interaction.guild.id)

        self.logs[guild_id] = channel.id
        save_logs(self.logs)

        embed = discord.Embed(
            title="📘 Message Log Channel Set",
            description=f"Message logs will now be sent to {channel.mention}",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)


    # ------------------ MESSAGE DELETE LOG ------------------
    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        if not message.guild:
            return

        if message.author.bot:
            return  # Ignore bot messages

        guild_id = str(message.guild.id)
        if guild_id not in self.logs:
            return  # Logging not set up

        log_channel = message.guild.get_channel(self.logs[guild_id])
        if not log_channel:
            return

        embed = discord.Embed(
            title="🗑️ Message Deleted",
            color=discord.Color.red()
        )
        embed.add_field(name="Author", value=message.author.mention, inline=True)
        embed.add_field(name="Channel", value=message.channel.mention, inline=True)
        embed.add_field(name="Content", value=message.content or "*No text content*", inline=False)
        embed.timestamp = message.created_at

        await log_channel.send(embed=embed)


    # ------------------ MESSAGE EDIT LOG ------------------
    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if not before.guild:
            return

        if before.author.bot:
            return  # Ignore bot messages

        if before.content == after.content:
            return  # No actual text change

        guild_id = str(before.guild.id)
        if guild_id not in self.logs:
            return  # Logging not set up

        log_channel = before.guild.get_channel(self.logs[guild_id])
        if not log_channel:
            return

        embed = discord.Embed(
            title="✏️ Message Edited",
            color=discord.Color.orange()
        )
        embed.add_field(name="Author", value=before.author.mention, inline=True)
        embed.add_field(name="Channel", value=before.channel.mention, inline=True)

        embed.add_field(
            name="Before",
            value=before.content or "*No text content*",
            inline=False
        )

        embed.add_field(
            name="After",
            value=after.content or "*No text content*",
            inline=False
        )

        embed.timestamp = after.edited_at or discord.utils.utcnow()

        await log_channel.send(embed=embed)


# Setup function required for cogs
async def setup(bot):
    await bot.add_cog(Logs(bot))


# ------------------ Status Loop ------------------
@tasks.loop(minutes=10)
async def update_status():
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name=f"Helping {len(bot.guilds)} servers"
        )
    )


# ------------------ Events ------------------
@bot.event
async def on_ready():
    if not update_status.is_running():
        update_status.start()

    await bot.tree.sync()
    print(f"Logged in as {bot.user} — Slash commands synced!")


# ------------------ Run Bot ------------------
TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable not set.")

bot.run(TOKEN)
