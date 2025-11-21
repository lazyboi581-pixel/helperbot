# bot.py — FULLY FIXED VERSION (PART 1)

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
from discord.ui import View, Button, Select

# ------------------ OWNER ID ------------------
OWNER_ID = 1382858887786528803  

# ------------------ Flask Keep-Alive ------------------

# update 1
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
# WARN SYSTEM
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


# ------------------ BLACKLIST SYSTEM ------------------
BLACKLIST_FILE = "blacklist.json"

def load_blacklist():
    if not os.path.exists(BLACKLIST_FILE):
        with open(BLACKLIST_FILE, "w") as f:
            json.dump([], f)
    with open(BLACKLIST_FILE, "r") as f:
        return json.load(f)

def save_blacklist(data):
    with open(BLACKLIST_FILE, "w") as f:
        json.dump(data, f, indent=4)

blacklisted_users = load_blacklist()


# ------------------ GLOBAL BLACKLIST CHECK ------------------
@bot.check
async def blacklist_check(interaction_or_ctx):

    # Slash command interactions
    if hasattr(interaction_or_ctx, "interaction") and interaction_or_ctx.interaction:
        user = interaction_or_ctx.interaction.user
        respond = interaction_or_ctx.interaction.response
    else:
        # fallback for future message commands
        user = interaction_or_ctx.author
        respond = interaction_or_ctx.respond

    # Check if blacklisted
    if user.id in blacklisted_users:

        # DM them
        try:
            await user.send("❌ You are banned from using Helper Bot.")
        except:
            pass

        # Ephemeral block message
        try:
            await respond.send_message(
                "❌ You are banned from using this bot.",
                ephemeral=True
            )
        except:
            pass

        return False

    return True


# ------------------ Permission Helpers ------------------
    
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
        title="🏓 Pong!",
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


# ------------------ Meme Command ------------------
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


# ------------------ Cute Command ------------------
@bot.tree.command(name="cute", description="Get a cute dog or cat picture")
@app_commands.describe(animal="Choose dog or cat")
async def cute(interaction: discord.Interaction, animal: str):

    animal = animal.lower()
    await interaction.response.defer()

    url = None
    if animal == "dog":
        url = "https://dog.ceo/api/breeds/image/random"
    elif animal == "cat":
        url = "https://api.thecatapi.com/v1/images/search"
    else:
        return await interaction.followup.send("Choose either 'dog' or 'cat'.")

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                return await interaction.followup.send("Could not fetch image.")

            data = await resp.json()

            if animal == "dog":
                img = data["message"]
            else:
                img = data[0]["url"]

            embed = discord.Embed(
                title=f"Here's a cute {animal}! 🐾",
                color=discord.Color.random()
            )
            embed.set_image(url=img)
            await interaction.followup.send(embed=embed)


# ------------------ Emoticons Command ------------------
@bot.tree.command(name="emoticons", description="Browse a list of emoticons that are easy to copy")
async def emoticons(interaction: discord.Interaction):

    emoticons_map = {
        "Cute": ["╰(°▽°)╯", "ヾ(≧▽≦*)o", "(p≧w≦q)", "(づ｡◕‿‿◕｡)づ", "(≧◡≦)", "(>ᴗ<)", "(｡♥‿♥｡)"],
        "Happy": ["（＾▽＾）", "ヽ(・∀・)ﾉ", "(＾▽＾)", "(*´▽`*)", "(*^‿^*)", "٩(◕‿◕｡)۶"],
        "Angry": ["(｀皿´＃)", "(ಠ_ಠ)", "(ง'̀-'́)ง", "(ノಠ益ಠ)ノ彡┻━┻", "(╬ Ò﹏Ó)"],
        "Crying": ["(ಥ﹏ಥ)", "(T_T)", "(；⌣̀_⌣́)", "(っ˘̩╭╮˘̩)っ", "(╥_╥)"],
        "Shrug": ["¯\\_(ツ)_/¯", "┐(￣ヘ￣)┌", "┐(´д｀)┌", "ʅ（◞‿◟）ʃ"],
        "Tableflip": ["(╯°□°）╯︵ ┻━┻", "┻━┻ ︵ヽ(`Д´)ﾉ︵ ┻━┻", "┬─┬ ノ( ゜-゜ノ)"]
    }

    class EmoteSelect(Select):
        def __init__(self, category):
            options = [
                discord.SelectOption(label=e, description="Tap to copy")
                for e in emoticons_map[category]
            ]
            super().__init__(
                placeholder="Select an emoticon",
                options=options,
                min_values=1,
                max_values=1
            )

        async def callback(self, i2: discord.Interaction):
            chosen = self.values[0]
            await i2.response.send_message(f"Here you go!\n\n`{chosen}`", ephemeral=True)

    class CategorySelect(Select):
        def __init__(self):
            options = [
                discord.SelectOption(label=c, description=f"{c} emoticons")
                for c in emoticons_map
            ]
            super().__init__(
                placeholder="Choose a category",
                options=options,
                min_values=1,
                max_values=1
            )

        async def callback(self, i2: discord.Interaction):
            category = self.values[0]
            view2 = View()
            view2.add_item(EmoteSelect(category))

            embed = discord.Embed(
                title=f"{category} Emoticons",
                description="Pick one below to copy it.",
                color=discord.Color.random()
            )
            await i2.response.edit_message(embed=embed, view=view2)

    view = View()
    view.add_item(CategorySelect())

    embed = discord.Embed(
        title="Emoticon Browser",
        description="Choose a category to view and copy emoticons.",
        color=discord.Color.random()
    )

    await interaction.response.send_message(embed=embed, view=view)


# ------------------ GIVEAWAY SYSTEM ------------------

class GiveawayView(View):
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
        return await channel.send(f"😢 No entries for **{prize}**.")

    winner_list = random.sample(entries, min(winners, len(entries)))
    mentions = ", ".join(f"<@{u}>" for u in winner_list)

    await channel.send(f"🎉 Congrats {mentions}! You won **{prize}**!")


@bot.tree.command(name="giveawaystart", description="Start a giveaway")
@app_commands.describe(duration="Minutes", prize="Prize", winners="Number of winners")
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

    asyncio.create_task(
        giveaway_auto_end(msg, prize, winners, duration, view)
    )


async def giveaway_auto_end(message, prize, winners, duration, view):
    await asyncio.sleep(duration * 60)
    await end_giveaway(message, prize, winners, view.entries)


@bot.tree.command(name="giveawayend", description="End a giveaway early")
@app_commands.describe(message_id="Giveaway message ID")
async def giveaway_end(interaction: discord.Interaction, message_id: str):
    try:
        msg = await interaction.channel.fetch_message(int(message_id))
    except Exception:
        return await interaction.response.send_message("Invalid message ID.", ephemeral=True)

    if not msg.components:
        return await interaction.response.send_message("That message has no giveaway.", ephemeral=True)

    view = msg.components[0].children[0].view

    await end_giveaway(msg, view.prize, view.winners, view.entries)
    await interaction.response.send_message("Giveaway ended!", ephemeral=True)


# ------------------ POLL SYSTEM ------------------
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
        name="Options:",
        value="\n".join(f"{emojis[i]} {options[i]}" for i in range(len(options))),
        inline=False
    )
    embed.set_footer(text=f"Poll ends in {duration}s")

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
    result_embed.add_field(name="Outcome:", value=result_text, inline=False)

    await interaction.followup.send(embed=result_embed)


from discord.ui import View, Button

# ------------------ Help Command (Auto-Updating + Buttons) ------------------

@bot.tree.command(name="help", description="Show the help menu with pages.")
async def help_command(interaction: discord.Interaction):

    # Auto detect commands
    fun_cmds = []
    moderation_cmds = []
    utility_cmds = []

    for cmd in bot.tree.get_commands():

        if cmd.name in ["hello", "joke", "corndog", "randomnumber", "compliment", "ping", "flip", "eight_ball", "8ball", "cute"]:
            fun_cmds.append(f"`/{cmd.name}`")

        elif cmd.name in ["kick", "ban", "unban", "timeout", "untimeout", "purge", "lock", "unlock", "warn", "clearwarns", "delwarn", "warns"]:
            moderation_cmds.append(f"`/{cmd.name}`")

        else:
            utility_cmds.append(f"`/{cmd.name}`")

    # Pages
    pages = []

    # Page 1 - Fun
    embed1 = discord.Embed(
        title="📘 Help Menu — Page 1/3",
        description="🎉 **Fun Commands**",
        color=discord.Color.blue()
    )
    embed1.add_field(name="Commands", value="\n".join(fun_cmds) if fun_cmds else "None", inline=False)
    embed1.set_footer(text="Use ◀️▶️ to switch pages")
    pages.append(embed1)

    # Page 2 - Moderation
    embed2 = discord.Embed(
        title="📘 Help Menu — Page 2/3",
        description="🔧 **Moderation Commands**",
        color=discord.Color.blurple()
    )
    embed2.add_field(name="Commands", value="\n".join(moderation_cmds) if moderation_cmds else "None", inline=False)
    embed2.set_footer(text="Use ◀️▶️ to switch pages")
    pages.append(embed2)

    # Page 3 - Utility
    embed3 = discord.Embed(
        title="📘 Help Menu — Page 3/3",
        description="🛠 **Utility Commands**",
        color=discord.Color.green()
    )
    embed3.add_field(name="Commands", value="\n".join(utility_cmds) if utility_cmds else "None", inline=False)
    embed3.set_footer(text="Use ◀️▶️ to switch pages")
    pages.append(embed3)

    # Buttons
    class HelpView(View):
        def __init__(self):
            super().__init__(timeout=60)
            self.page = 0

            # Bottom Link Buttons
            self.add_item(Button(label="Support Server", url="https://discord.gg/7mSV6kENz3"))
            self.add_item(Button(label="Terms of Service", url="https://helper-bot-tos.carrd.co/"))
            self.add_item(Button(label="Privacy Policy", url="https://helper-bot-privacy-policy.carrd.co/"))

        @discord.ui.button(label="◀️", style=discord.ButtonStyle.blurple)
        async def previous(self, interaction2: discord.Interaction, button: Button):
            self.page = (self.page - 1) % len(pages)
            await interaction2.response.edit_message(embed=pages[self.page], view=self)

        @discord.ui.button(label="▶️", style=discord.ButtonStyle.blurple)
        async def next(self, interaction2: discord.Interaction, button: Button):
            self.page = (self.page + 1) % len(pages)
            await interaction2.response.edit_message(embed=pages[self.page], view=self)

    view = HelpView()

    await interaction.response.send_message(embed=pages[0], view=view)


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

# ------------------ Emoticons Command (Mobile + Desktop Friendly) ------------------

@bot.tree.command(name="emoticons", description="Browse an emoticon list that is easy to copy on mobile and desktop.")
async def emoticons(interaction: discord.Interaction):

    # Emoticon categories
    emoticons = {
        "Cute": [
            "╰(°▽°)╯",
            "ヾ(≧▽≦*)o",
            "(p≧w≦q)",
            "(づ｡◕‿‿◕｡)づ",
            "(≧◡≦)",
            "(>ᴗ<)",
            "(｡♥‿♥｡)"
        ],
        "Happy": [
            "（＾▽＾）",
            "ヽ(・∀・)ﾉ",
            "(＾▽＾)",
            "(*´▽`*)",
            "(*^‿^*)",
            "٩(◕‿◕｡)۶"
        ],
        "Angry": [
            "(｀皿´＃)",
            "(ಠ_ಠ)",
            "(ง'̀-'́)ง",
            "(ノಠ益ಠ)ノ彡┻━┻",
            "(╬ Ò﹏Ó)"
        ],
        "Crying": [
            "(ಥ﹏ಥ)",
            "(T_T)",
            "(；⌣̀_⌣́)",
            "(っ˘̩╭╮˘̩)っ",
            "(╥_╥)"
        ],
        "Shrug": [
            "¯\\_(ツ)_/¯",
            "┐(￣ヘ￣)┌",
            "┐(´д｀)┌",
            "ʅ（◞‿◟）ʃ"
        ],
        "Tableflip": [
            "(╯°□°）╯︵ ┻━┻",
            "┻━┻ ︵ヽ(`Д´)ﾉ︵ ┻━┻",
            "┬─┬ ノ( ゜-゜ノ)"
        ]
    }

    # Second dropdown (emoticons list)
    class EmoteSelect(Select):
        def __init__(self, category):
            options = [
                discord.SelectOption(label=e, description="Click to copy") 
                for e in emoticons[category]
            ]
            super().__init__(
                placeholder="Select an emoticon to copy",
                options=options,
                min_values=1,
                max_values=1
            )

        async def callback(self, interaction2: discord.Interaction):
            chosen = self.values[0]
            await interaction2.response.send_message(
                f"Here you go!\n\n**`{chosen}`**\n\n(You can copy it easily on mobile & desktop)",
                ephemeral=True
            )

    # First dropdown (category)
    class CategorySelect(Select):
        def __init__(self):
            options = [
                discord.SelectOption(label=c, description=f"{c} emoticons")
                for c in emoticons
            ]
            super().__init__(
                placeholder="Choose a category...",
                options=options,
                min_values=1,
                max_values=1
            )

        async def callback(self, interaction2: discord.Interaction):
            category = self.values[0]

            # new view for emoticons list
            view2 = View()
            view2.add_item(EmoteSelect(category))

            embed = discord.Embed(
                title=f"{category} Emoticons",
                description="Select an emoticon below to copy it.",
                color=discord.Color.random()
            )

            await interaction2.response.edit_message(embed=embed, view=view2)

    view = View()
    view.add_item(CategorySelect())

    embed = discord.Embed(
        title="(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧ Emoticon Browser",
        description="Choose a category to browse emoticons!",
        color=discord.Color.random()
    )

    await interaction.response.send_message(embed=embed, view=view)

# ------------------ Moderation Commands ------------------

@bot.event
async def on_automod_action_execution(payload: discord.AutoModAction):
    guild_id = str(payload.guild_id)

    if guild_id not in modlog_data:
        return  # No mod-log for this server yet

    channel_id = modlog_data[guild_id]
    guild = bot.get_guild(payload.guild_id)
    channel = guild.get_channel(channel_id)

    if not channel:
        return

    embed = discord.Embed(
        title="⚠️ AutoMod Triggered",
        color=discord.Color.red()
    )

    embed.add_field(name="User", value=f"<@{payload.user_id}>")
    embed.add_field(name="Rule", value=payload.rule_name)
    embed.add_field(name="Action", value=str(payload.action.type).replace("AutoModRuleActionType.", ""))
    embed.add_field(name="Blocked Message?", value="Yes" if payload.blocked_message else "No")
    embed.set_timestamp()

    await channel.send(embed=embed)


@bot.tree.command(name="automod_setup", description="Enable AutoMod with blocking, timeout, and logging")
async def automod_setup(interaction: discord.Interaction):

    if not interaction.user.guild_permissions.manage_guild:
        return await interaction.response.send_message(
            "❌ You need Manage Server to use this command.",
            ephemeral=True
        )

    guild = interaction.guild
    guild_id = str(guild.id)

    await interaction.response.send_message("⏳ Setting up AutoMod…", ephemeral=True)

    # Keyword block rule
    try:
        await guild.create_automod_rule(
            name="Bad Words Filter",
            event_type=discord.AutoModRuleEventType.MESSAGE_SEND,
            trigger=discord.AutoModRuleTrigger(
                type=discord.AutoModRuleTriggerType.KEYWORD,
                keyword_filter=[
                    "fuck", "shit", "bitch", "nigger", "faggot",
                    "slur1", "slur2", "cunt", "whore"
                ]
            ),
            actions=[
                discord.AutoModRuleAction(type=discord.AutoModRuleActionType.BLOCK_MESSAGE),
                discord.AutoModRuleAction(type=discord.AutoModRuleActionType.TIMEOUT, duration_seconds=60)
            ],
            enabled=True
        )
    except:
        pass

    # Mass mention filter
    try:
        await guild.create_automod_rule(
            name="Mass Mentions",
            event_type=discord.AutoModRuleEventType.MESSAGE_SEND,
            trigger=discord.AutoModRuleTrigger(
                type=discord.AutoModRuleTriggerType.MENTION_SPAM,
                mention_total_limit=4
            ),
            actions=[
                discord.AutoModRuleAction(type=discord.AutoModRuleActionType.BLOCK_MESSAGE),
                discord.AutoModRuleAction(type=discord.AutoModRuleActionType.TIMEOUT, duration_seconds=120)
            ],
            enabled=True
        )
    except:
        pass

    # Invite blocker
    try:
        await guild.create_automod_rule(
            name="Block Invites",
            event_type=discord.AutoModRuleEventType.MESSAGE_SEND,
            trigger=discord.AutoModRuleTrigger(
                type=discord.AutoModRuleTriggerType.KEYWORD,
                keyword_filter=["discord.gg/", "discord.com/invite", "invite.gg"]
            ),
            actions=[
                discord.AutoModRuleAction(type=discord.AutoModRuleActionType.BLOCK_MESSAGE)
            ],
            enabled=True
        )
    except:
        pass

    await interaction.followup.send(
        "✅ AutoMod Enabled!\n"
        "- Bad words blocked\n"
        "- Invites blocked\n"
        "- Mass mentions blocked\n"
        "- Users timed out\n"
        "- Logged to mod-log channel\n\n"
        "Use `/setmodlog` to change the log channel.",
        ephemeral=True
    )


@bot.tree.command(name="setmodlog", description="Choose the mod-log channel for this server")
async def setmodlog(interaction: discord.Interaction, channel: discord.TextChannel):

    # Admin/Owner check
    if not interaction.user.guild_permissions.manage_guild:
        return await interaction.response.send_message(
            "❌ You need **Manage Server** to use this.", ephemeral=True
        )

    guild_id = str(interaction.guild.id)

    modlog_data[guild_id] = channel.id
    save_modlogs(modlog_data)

    await interaction.response.send_message(
        f"✅ Mod-log channel has been set to {channel.mention}",
        ephemeral=True
    )


# Universal per-server mod-log storage
MODLOG_FILE = "modlogs.json"

def load_modlogs():
    if not os.path.exists(MODLOG_FILE):
        with open(MODLOG_FILE, "w") as f:
            json.dump({}, f)
    with open(MODLOG_FILE, "r") as f:
        return json.load(f)

def save_modlogs(data):
    with open(MODLOG_FILE, "w") as f:
        json.dump(data, f, indent=4)

modlog_data = load_modlogs()


@bot.tree.command(name="automod_setup", description="Set up REAL Discord AutoMod with timeout + logging")
async def automod_setup(interaction: discord.Interaction):

    # ----------------------------------------------------
    # PERMISSION CHECK
    # ----------------------------------------------------
    if not interaction.user.guild_permissions.manage_guild:
        return await interaction.response.send_message(
            "❌ You must have **Manage Server** to use this command.",
            ephemeral=True
        )

    guild = interaction.guild

    await interaction.response.send_message("⏳ Setting up AutoMod rules…", ephemeral=True)

    # ----------------------------------------------------
    # 1. KEYWORD RULE (BAD WORDS)
    # ----------------------------------------------------
    try:
        await guild.create_automod_rule(
            name="Bad Words Filter",
            event_type=discord.AutoModRuleEventType.MESSAGE_SEND,
            trigger=discord.AutoModRuleTrigger(
                type=discord.AutoModRuleTriggerType.KEYWORD,
                keyword_filter=[
                    "fuck", "shit", "bitch", "nigger", "faggot",
                    "slur1", "slur2", "cunt", "whore"
                ]
            ),
            actions=[
                discord.AutoModRuleAction(type=discord.AutoModRuleActionType.BLOCK_MESSAGE),
                discord.AutoModRuleAction(type=discord.AutoModRuleActionType.TIMEOUT, duration_seconds=60)
            ],
            enabled=True
        )
    except:
        pass

    # ----------------------------------------------------
    # 2. MASS MENTION FILTER
    # ----------------------------------------------------
    try:
        await guild.create_automod_rule(
            name="Mass Mentions",
            event_type=discord.AutoModRuleEventType.MESSAGE_SEND,
            trigger=discord.AutoModRuleTrigger(
                type=discord.AutoModRuleTriggerType.MENTION_SPAM,
                mention_total_limit=4
            ),
            actions=[
                discord.AutoModRuleAction(type=discord.AutoModRuleActionType.BLOCK_MESSAGE),
                discord.AutoModRuleAction(type=discord.AutoModRuleActionType.TIMEOUT, duration_seconds=120)
            ],
            enabled=True
        )
    except:
        pass

    # ----------------------------------------------------
    # 3. INVITE BLOCKER
    # ----------------------------------------------------
    try:
        await guild.create_automod_rule(
            name="Block Invites",
            event_type=discord.AutoModRuleEventType.MESSAGE_SEND,
            trigger=discord.AutoModRuleTrigger(
                type=discord.AutoModRuleTriggerType.KEYWORD,
                keyword_filter=["discord.gg/", "invite.gg", "discord.com/invite"]
            ),
            actions=[
                discord.AutoModRuleAction(type=discord.AutoModRuleActionType.BLOCK_MESSAGE),
            ],
            enabled=True
        )
    except:
        pass

    # ----------------------------------------------------
    # 4. LOGGING AUTOMOD ACTIONS
    # ----------------------------------------------------
    @bot.event
    async def on_automod_action_execution(payload: discord.AutoModAction):
        try:
            channel = guild.get_channel(MODLOG_CHANNEL_ID)
            if not channel:
                return

            embed = discord.Embed(
                title="⚠️ AutoMod Action Triggered",
                color=discord.Color.red()
            )
            embed.add_field(name="User", value=f"<@{payload.user_id}>")
            embed.add_field(name="Rule", value=payload.rule_name)
            embed.add_field(name="Action", value=str(payload.action.type).replace("AutoModRuleActionType.", ""))
            embed.add_field(name="Blocked Message?", value="Yes" if payload.blocked_message else "No")
            embed.set_timestamp()

            await channel.send(embed=embed)
        except Exception as e:
            print("LOG ERROR:", e)

    # ----------------------------------------------------
    # DONE
    # ----------------------------------------------------
    await interaction.followup.send(
        "✅ **AutoMod is now enabled for this server!**\n"
        "- Blocks bad words\n"
        "- Blocks invites\n"
        "- Blocks mass mentions\n"
        "- Auto-timeouts users\n"
        "- Logs actions in mod-logs",
        ephemeral=True
    )


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


@bot.tree.command(name="purge", description="Delete messages (1-100)")
async def purge(interaction: discord.Interaction, number: int):
    if not has_guild_permissions(interaction.user, manage_messages=True):
        return await interaction.response.send_message("Missing permission.", ephemeral=True)

    if number < 1 or number > 100:
        return await interaction.response.send_message("Enter 1-100.", ephemeral=True)

    await interaction.response.defer(ephemeral=True)
    deleted = await interaction.channel.purge(limit=number)
    await interaction.followup.send(f"Deleted {len(deleted)} messages.", ephemeral=True)


@bot.tree.command(name="lock", description="Lock the channel")
async def lock(interaction: discord.Interaction):
    if not has_guild_permissions(interaction.user, manage_channels=True):
        return await interaction.response.send_message("Missing permission.", ephemeral=True)

    await interaction.channel.set_permissions(interaction.guild.default_role, send_messages=False)
    await interaction.response.send_message("🔒 Channel locked.")


@bot.tree.command(name="unlock", description="Unlock the channel")
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
        "reason": reason or "No reason provided",
        "by": str(interaction.user),
        "timestamp": datetime.datetime.utcnow().isoformat()
    }

    data[guild_id][uid].append(warn_info)
    save_warns(data)

    await interaction.response.send_message(
        f"⚠️ Warned {member.mention}. Total warnings: {len(data[guild_id][uid])}"
    )


@bot.tree.command(name="warns", description="Check a member's warnings")
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


@bot.tree.command(name="clearwarns", description="Clear ALL warnings for a member")
async def clearwarns(interaction: discord.Interaction, member: discord.Member):
    if not has_guild_permissions(interaction.user, kick_members=True):
        return await interaction.response.send_message("Missing permission.", ephemeral=True)

    data = load_warns()
    guild_id = str(interaction.guild.id)
    uid = str(member.id)

    if guild_id in data and uid in data[guild_id]:
        data[guild_id][uid] = []
        save_warns(data)
        return await interaction.response.send_message(f"🗑 Cleared all warnings for {member.mention}")

    await interaction.response.send_message("This user has no warnings.", ephemeral=True)


@bot.tree.command(name="delwarn", description="Delete a single warning by number")
async def delwarn(interaction: discord.Interaction, member: discord.Member, warn_number: int):

    if not has_guild_permissions(interaction.user, kick_members=True):
        return await interaction.response.send_message("Missing permission.", ephemeral=True)

    data = load_warns()
    guild_id = str(interaction.guild.id)
    uid = str(member.id)

    if guild_id not in data or uid not in data[guild_id]:
        return await interaction.response.send_message("This user has no warnings.", ephemeral=True)

    warns_list = data[guild_id][uid]

    if warn_number < 1 or warn_number > len(warns_list):
        return await interaction.response.send_message("Invalid warning number.", ephemeral=True)

    removed = warns_list.pop(warn_number - 1)
    save_warns(data)

    await interaction.response.send_message(
        f"🗑 Removed warning #{warn_number} from {member.mention}\nReason: {removed['reason']}"
    )

    
# ------------------ BLACKLIST SYSTEM ------------------
BLACKLIST_FILE = "blacklist.json"

def load_blacklist():
    if not os.path.exists(BLACKLIST_FILE):
        with open(BLACKLIST_FILE, "w") as f:
            json.dump([], f)
    with open(BLACKLIST_FILE, "r") as f:
        return json.load(f)

def save_blacklist(data):
    with open(BLACKLIST_FILE, "w") as f:
        json.dump(data, f, indent=4)

blacklisted_users = load_blacklist()


# ------------------ BOT OWNER BLACKLIST COMMANDS ------------------

@bot.tree.command(name="botban", description="Ban a user from using the bot.")
@app_commands.describe(user="User to blacklist")
async def botban(interaction: discord.Interaction, user: discord.User):

    if interaction.user.id != OWNER_ID:
        return await interaction.response.send_message("❌ Only the bot owner can use this.", ephemeral=True)

    if user.id in blacklisted_users:
        return await interaction.response.send_message("User already banned.", ephemeral=True)

    blacklisted_users.append(user.id)
    save_blacklist(blacklisted_users)

    await interaction.response.send_message(
        f"🚫 {user} is now banned from using this bot.",
        ephemeral=True
    )


@bot.tree.command(name="botunban", description="Unban a user from the bot.")
@app_commands.describe(user="User to unban")
async def botunban(interaction: discord.Interaction, user: discord.User):

    if interaction.user.id != OWNER_ID:
        return await interaction.response.send_message("❌ Only the bot owner can use this.", ephemeral=True)

    if user.id not in blacklisted_users:
        return await interaction.response.send_message("User is not banned.", ephemeral=True)

    blacklisted_users.remove(user.id)
    save_blacklist(blacklisted_users)

    await interaction.response.send_message(
        f"✅ {user} has been unbanned.",
        ephemeral=True
    )


@bot.tree.command(name="botbanlist", description="View all banned bot users.")
async def botbanlist(interaction: discord.Interaction):

    if interaction.user.id != OWNER_ID:
        return await interaction.response.send_message("❌ Only the bot owner can use this.", ephemeral=True)

    if not blacklisted_users:
        return await interaction.response.send_message("No banned users.", ephemeral=True)

    formatted = "\n".join(f"• <@{uid}> (`{uid}`)" for uid in blacklisted_users)

    await interaction.response.send_message(
        f"🚫 **Blacklisted Users:**\n{formatted}",
        ephemeral=True
    )


# ------------------ Status Loop ------------------
@tasks.loop(minutes=10)
async def update_status():
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.playing,
            name=f"/help | Helping {len(bot.guilds)} servers"
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
    raise RuntimeError("BOT_TOKEN env var missing.")

bot.run(TOKEN)
