import os
import asyncio
import random
import discord
from discord.ext import commands

# ============================================================
# CONFIG
# ============================================================

TOKEN = os.getenv("DISCORD_TOKEN")

# YOUR DISCORD USER ID
OWNER_ID = 494442502632243200

# ROLE IDS
SELLER_ROLE_ID = 1541096480146853968
BUYER_ROLE_ID = 1541096480146853968
MIDDLEMAN_ROLE_ID = 1541096469669351424

# CHANNEL WHERE THE AUTOMATIC POSTS GO
VOUCH_CHANNEL_ID = 1541096647218692176

# 10 MINUTES
VOUCH_COOLDOWN = 10 * 60

# ============================================================
# PHOTOS
# ============================================================

VOUCH_PHOTOS = [
    "https://i.imgur.com/ggWdeJm.png",
    "https://i.imgur.com/NkISKXf.png",
    "https://i.imgur.com/hJ7AS11.png",
    "https://i.imgur.com/JizEvDP.png",
    "https://i.imgur.com/fTWzkr3.png",
    "https://i.imgur.com/gK7QXeO.png",
    "https://i.imgur.com/7SUZCY8.png",
    "https://i.imgur.com/h1wbgMx.png",
    "https://i.imgur.com/OJZPuds.png",
    "https://i.imgur.com/YT57LBt.png"
]

# ============================================================
# TRADE TYPES
# ============================================================

TRADE_TYPES = [
    "LTC ↔ Ingame",
    "Robux ↔ Ingame",
    "PayPal ↔ Ingame",
    "Cash App ↔ Ingame",
    "Gift Card ↔ Ingame",
    "Ingame ↔ Ingame"
]

# ============================================================
# DEMO FEEDBACK
# ============================================================

FEEDBACK_COMMENTS = [
    "Demo feedback — testing only.",
    "Example feedback — testing only.",
    "Demo trade example.",
    "Automated test activity.",
    "Sample activity — not a real vouch.",
    "Testing the trade activity system."
]

# ============================================================
# BOT SETUP
# ============================================================

intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

vouch_running = False
vouch_task = None

# ============================================================
# MIDDLEMAN ROTATION
# ============================================================

middleman_index = 0


# ============================================================
# READY
# ============================================================

@bot.event
async def on_ready():
    print(f"✅ {bot.user} is online!")
    print(f"Bot ID: {bot.user.id}")
    print("✅ 10-minute cooldown enabled.")
    print("✅ Middleman rotation enabled.")


# ============================================================
# RANDOM MEMBER WITH ROLE
# ============================================================

def random_member_with_role(
    guild,
    role_id,
    exclude_ids=None
):

    role = guild.get_role(role_id)

    if role is None:
        return None

    if exclude_ids is None:
        exclude_ids = set()

    members = [
        member
        for member in role.members
        if not member.bot
        and member.id not in exclude_ids
    ]

    if not members:
        return None

    return random.choice(members)


# ============================================================
# ALTERNATING MIDDLEMAN
# ============================================================

def get_next_middleman(
    guild,
    exclude_ids=None
):

    global middleman_index

    role = guild.get_role(MIDDLEMAN_ROLE_ID)

    if role is None:
        return None

    if exclude_ids is None:
        exclude_ids = set()

    members = [
        member
        for member in role.members
        if not member.bot
        and member.id not in exclude_ids
    ]

    if not members:
        return None

    # Keep the rotation consistent
    members.sort(key=lambda member: member.id)

    # Select the current MM
    middleman = members[
        middleman_index % len(members)
    ]

    # Move to the next MM
    middleman_index += 1

    return middleman


# ============================================================
# SEND AUTOMATIC DEMO ACTIVITY
# ============================================================

async def send_trade_activity(guild):

    channel = guild.get_channel(
        VOUCH_CHANNEL_ID
    )

    if channel is None:
        print("❌ Vouch channel not found.")
        return

    # --------------------------------------------------------
    # RANDOM SELLER
    # --------------------------------------------------------

    seller = random_member_with_role(
        guild,
        SELLER_ROLE_ID
    )

    if seller is None:
        print("❌ No Seller found.")
        return

    # --------------------------------------------------------
    # RANDOM BUYER
    # --------------------------------------------------------

    buyer = random_member_with_role(
        guild,
        BUYER_ROLE_ID,
        {seller.id}
    )

    if buyer is None:
        print("❌ No Buyer found.")
        return

    # --------------------------------------------------------
    # ALTERNATING MIDDLEMAN
    # --------------------------------------------------------

    middleman = get_next_middleman(
        guild,
        {seller.id, buyer.id}
    )

    if middleman is None:
        print("❌ No Middleman found.")
        return

    # --------------------------------------------------------
    # RANDOM PHOTO
    # --------------------------------------------------------

    valid_photos = [
        photo
        for photo in VOUCH_PHOTOS
        if photo.startswith("http")
    ]

    if not valid_photos:
        print("❌ No valid photos found.")
        return

    photo = random.choice(valid_photos)

    # --------------------------------------------------------
    # RANDOM TRADE TYPE
    # --------------------------------------------------------

    trade_type = random.choice(
        TRADE_TYPES
    )

    # --------------------------------------------------------
    # DEMO FEEDBACK
    # --------------------------------------------------------

    feedback_1 = random.choice(
        FEEDBACK_COMMENTS
    )

    available_feedback = [
        comment
        for comment in FEEDBACK_COMMENTS
        if comment != feedback_1
    ]

    feedback_2 = random.choice(
        available_feedback
    )

    # --------------------------------------------------------
    # EMBED
    # --------------------------------------------------------

    embed = discord.Embed(
        title="🧪 Demo Trade Activity",
        description=(
            "⚠️ **DEMO / TESTING ONLY**\n"
            "This automated activity is not a real customer vouch."
        ),
        color=discord.Color.from_rgb(
            255,
            105,
            180
        )
    )

    # --------------------------------------------------------
    # TRADE TYPE
    # --------------------------------------------------------

    embed.add_field(
        name="Trade Type",
        value=f"`{trade_type}`",
        inline=False
    )

    # --------------------------------------------------------
    # USERS
    # --------------------------------------------------------

    embed.add_field(
        name="Users",
        value=(
            f"**Seller:** {seller.mention}\n"
            f"**Buyer:** {buyer.mention}\n"
            f"**MM:** {middleman.mention}"
        ),
        inline=False
    )

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    embed.add_field(
        name="Status",
        value="🧪 Demo / Testing",
        inline=False
    )

    # --------------------------------------------------------
    # FEEDBACK
    # --------------------------------------------------------

    embed.add_field(
        name="Demo Feedback",
        value=(
            f"⭐️⭐️⭐️⭐️⭐️\n"
            f"{feedback_1}\n\n"
            f"⭐️⭐️⭐️⭐️⭐️\n"
            f"{feedback_2}"
        ),
        inline=False
    )

    # --------------------------------------------------------
    # PHOTO
    # --------------------------------------------------------

    embed.set_image(
        url=photo
    )

    # --------------------------------------------------------
    # FOOTER
    # --------------------------------------------------------

    embed.set_footer(
        text="Demo Activity • Testing System"
    )

    # --------------------------------------------------------
    # PING SELLER + BUYER + ALTERNATING MM
    # --------------------------------------------------------

    content = (
        f"{seller.mention} "
        f"{buyer.mention} "
        f"{middleman.mention}"
    )

    await channel.send(
        content=content,
        embed=embed,
        allowed_mentions=discord.AllowedMentions(
            users=True
        )
    )

    print(
        "Demo activity sent: "
        f"{seller} / "
        f"{buyer} / "
        f"{middleman} / "
        f"{trade_type}"
    )


# ============================================================
# AUTOMATIC LOOP
# ============================================================

async def automatic_vouch_loop(guild):

    global vouch_running

    while vouch_running:

        try:

            await send_trade_activity(guild)

            # WAIT 10 MINUTES
            await asyncio.sleep(
                VOUCH_COOLDOWN
            )

        except asyncio.CancelledError:
            break

        except Exception as e:

            print(
                f"❌ Automatic system error: {e}"
            )

            await asyncio.sleep(10)


# ============================================================
# START VOUCH SYSTEM
# ============================================================

@bot.command(name="startvouch")
async def start_vouch(ctx):

    global vouch_running
    global vouch_task

    if ctx.author.id != OWNER_ID:

        await ctx.send(
            "❌ Only the bot owner can use this command."
        )

        return

    if vouch_running:

        await ctx.send(
            "⚠️ The automatic system is already running."
        )

        return

    vouch_running = True

    await ctx.send(
        "🟢 **Automatic Demo Activity Started**\n"
        "A new demo activity will be posted every "
        "**10 minutes**.\n"
        "Middlemen will be pinged alternately."
    )

    vouch_task = asyncio.create_task(
        automatic_vouch_loop(ctx.guild)
    )


# ============================================================
# STOP VOUCH SYSTEM
# ============================================================

@bot.command(name="stopvouch")
async def stop_vouch(ctx):

    global vouch_running
    global vouch_task

    if ctx.author.id != OWNER_ID:

        await ctx.send(
            "❌ Only the bot owner can use this command."
        )

        return

    if not vouch_running:

        await ctx.send(
            "⚠️ The automatic system isn't running."
        )

        return

    vouch_running = False

    if vouch_task:

        vouch_task.cancel()
        vouch_task = None

    await ctx.send(
        "🔴 **Automatic Demo Activity Stopped**"
    )


# ============================================================
# STATUS
# ============================================================

@bot.command(name="vouchstatus")
async def vouch_status(ctx):

    if ctx.author.id != OWNER_ID:

        await ctx.send(
            "❌ Only the bot owner can use this command."
        )

        return

    if vouch_running:

        await ctx.send(
            "🟢 **Status:** Running\n"
            "⏱️ **Interval:** 10 minutes\n"
            "🔄 **Middleman:** Alternating"
        )

    else:

        await ctx.send(
            "🔴 **Status:** Stopped"
        )


# ============================================================
# ERROR HANDLER
# ============================================================

@bot.event
async def on_command_error(ctx, error):

    if isinstance(
        error,
        commands.CommandNotFound
    ):
        return

    print(
        f"Command error: {error}"
    )


# ============================================================
# RUN
# ============================================================

bot.run(TOKEN)
