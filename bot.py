import os
import asyncio
import random
import json
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

# OWNER ROLE
OWNER_ROLE_ID = 1541779938930065498

# CHANNEL WHERE THE AUTOMATIC POSTS GO
VOUCH_CHANNEL_ID = 1541096647218692176

# CUSTOM EMOJIS
STAR_EMOJI = "<:starz:1544307175340511285>"
CHECK_EMOJI = "<:check:1544306907768946780>"

# ============================================================
# 10 MINUTES COOLDOWN
# ============================================================

VOUCH_COOLDOWN = 10 * 60

# ============================================================
# PERMANENT VOUCH PHOTO FILE
# ============================================================

VOUCH_PHOTOS_FILE = "/app/data/vouch_photos.json"

# ============================================================
# VOUCH PHOTOS - 26 TOTAL
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
    "https://i.imgur.com/YT57LBt.png",
    "https://i.imgur.com/epPTBBA.png",
    "https://i.imgur.com/IOmc9Ry.png",
    "https://i.imgur.com/Jv6vJvd.png",
    "https://i.imgur.com/HgxkgRQ.png",
    "https://i.imgur.com/h6gCX9L.png",
    "https://i.imgur.com/iZGKoTg.png",
    "https://i.imgur.com/v8CYWgo.png",
    "https://i.imgur.com/awLPcEG.png",
    "https://i.imgur.com/vGYOIlM.png",
    "https://i.imgur.com/JNfCO5b.png",
    "https://i.imgur.com/sN52n9r.png",
    "https://i.imgur.com/HKbvv9G.png",
    "https://i.imgur.com/h1WWmDF.png",
    "https://i.imgur.com/kj6NSof.png",
    "https://i.imgur.com/fL2fDbr.png",
    "https://i.imgur.com/Es7MsLb.png"
]

# ============================================================
# LOAD SAVED VOUCH PHOTOS
# ============================================================

def load_vouch_photos():

    global VOUCH_PHOTOS

    try:

        if os.path.exists(VOUCH_PHOTOS_FILE):

            with open(
                VOUCH_PHOTOS_FILE,
                "r",
                encoding="utf-8"
            ) as file:

                saved_photos = json.load(file)

            if isinstance(saved_photos, list):

                for photo in saved_photos:

                    if (
                        isinstance(photo, str)
                        and photo.startswith("http")
                        and photo not in VOUCH_PHOTOS
                    ):

                        VOUCH_PHOTOS.append(photo)

                print(
                    f"📸 Loaded {len(saved_photos)} saved vouch photos."
                )

    except Exception as e:

        print(
            f"❌ Could not load vouch photos: {e}"
        )


# ============================================================
# SAVE VOUCH PHOTOS
# ============================================================

def save_vouch_photos():

    try:

        with open(
            VOUCH_PHOTOS_FILE,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                VOUCH_PHOTOS,
                file,
                indent=4
            )

        print(
            f"💾 Saved {len(VOUCH_PHOTOS)} vouch photos."
        )

    except Exception as e:

        print(
            f"❌ Could not save vouch photos: {e}"
        )


# Load saved pictures when bot starts
load_vouch_photos()

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
# SAMPLE FEEDBACK
# ============================================================

FEEDBACK_COMMENTS = [
    "okay experience overall.",
    "okay deal, slow responses.",
    "great experience overall.",
    "fast responses.",
    "smooth trade.",
    "quick and easy trade.",
    "good service.",
    "everything went smoothly.",
    "easy trade, no problems.",
    "fast and simple.",
    "good deal.",
    "reliable service."
]

# ============================================================
# BOT SETUP
# ============================================================

intents = discord.Intents.default()

intents.guilds = True
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix="$",
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
    print("⏱️ Vouch cooldown: 10 minutes")
    print("🔄 Middleman rotation: enabled")
    print(
        f"📸 Vouch photos loaded: {len(VOUCH_PHOTOS)}"
    )


# ============================================================
# FIND RANDOM MEMBER WITH ROLE
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
# GET NEXT MIDDLEMAN
# ============================================================

def get_next_middleman(
    guild,
    exclude_ids=None
):

    global middleman_index

    role = guild.get_role(
        MIDDLEMAN_ROLE_ID
    )

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

    members.sort(
        key=lambda member: member.id
    )

    middleman = members[
        middleman_index % len(members)
    ]

    middleman_index += 1

    return middleman


# ============================================================
# SEND AUTOMATIC TRADE ACTIVITY
# ============================================================

async def send_trade_activity(guild):

    channel = guild.get_channel(
        VOUCH_CHANNEL_ID
    )

    if channel is None:

        print(
            "❌ Vouch channel not found."
        )

        return

    # --------------------------------------------------------
    # RANDOM SELLER
    # --------------------------------------------------------

    seller = random_member_with_role(
        guild,
        SELLER_ROLE_ID
    )

    if seller is None:

        print(
            "❌ No Seller found."
        )

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

        print(
            "❌ No Buyer found."
        )

        return

    # --------------------------------------------------------
    # ALTERNATING MIDDLEMAN
    # --------------------------------------------------------

    middleman = get_next_middleman(
        guild,
        {seller.id, buyer.id}
    )

    if middleman is None:

        print(
            "❌ No Middleman found."
        )

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

        print(
            "❌ No valid vouch photos found."
        )

        return

    photo = random.choice(
        valid_photos
    )

    # --------------------------------------------------------
    # RANDOM TRADE TYPE
    # --------------------------------------------------------

    trade_type = random.choice(
        TRADE_TYPES
    )

    # --------------------------------------------------------
    # RANDOM SAMPLE FEEDBACK
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

    stars_1 = random.randint(
        3,
        5
    )

    stars_2 = random.randint(
        3,
        5
    )

    star_text_1 = STAR_EMOJI * stars_1
    star_text_2 = STAR_EMOJI * stars_2

    # --------------------------------------------------------
    # EMBED
    # --------------------------------------------------------

    embed = discord.Embed(
        title=f"{CHECK_EMOJI} Verified Vouch",
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
        value=f"`{trade_type}'\n\n"
        inline=False
    )

    # EXTRA SPACING
    embed.add_field(
        name="\u200b",
        value="\n",
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
            f"**MM:** {middleman.mention}\n\n"
        ),
        inline=False
    )

    # EXTRA SPACING
    embed.add_field(
        name="\u200b",
        value="\n",
        inline=False
    )

    # --------------------------------------------------------
    # FEEDBACK
    # --------------------------------------------------------

    embed.add_field(
        name="Feedback",
        value=(
            f"{star_text_1}\n"
            f"{feedback_1}\n\n"
            f"{star_text_2}\n"
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
    # PING SELLER + BUYER + MIDDLEMAN
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
        f"Trade activity sent: "
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

            await send_trade_activity(
                guild
            )

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
# OWNER ROLE ONLY
# ============================================================

@bot.command(
    name="startvouch"
)
async def start_vouch(ctx):

    global vouch_running
    global vouch_task

    # --------------------------------------------------------
    # CHECK OWNER ROLE
    # --------------------------------------------------------

    owner_role = ctx.guild.get_role(
        OWNER_ROLE_ID
    )

    if owner_role is None:

        await ctx.send(
            "❌ Owner role not found."
        )

        return

    if owner_role not in ctx.author.roles:

        await ctx.send(
            "❌ Only members with the **Owner** role can use this command."
        )

        return

    # --------------------------------------------------------
    # CHECK STATUS
    # --------------------------------------------------------

    if vouch_running:

        await ctx.send(
            "⚠️ The automatic system is already running."
        )

        return

    # --------------------------------------------------------
    # START
    # --------------------------------------------------------

    vouch_running = True

    await ctx.send(
        "🟢 **Automatic Trade Activity Started**\n"
        "A new activity will be posted every "
        "**10 minutes**.\n"
        "Middlemen will be pinged alternately."
    )

    vouch_task = asyncio.create_task(
        automatic_vouch_loop(
            ctx.guild
        )
    )


# ============================================================
# STOP VOUCH SYSTEM
# OWNER ROLE ONLY
# ============================================================

@bot.command(
    name="stopvouch"
)
async def stop_vouch(ctx):

    global vouch_running
    global vouch_task

    # --------------------------------------------------------
    # CHECK OWNER ROLE
    # --------------------------------------------------------

    owner_role = ctx.guild.get_role(
        OWNER_ROLE_ID
    )

    if owner_role is None:

        await ctx.send(
            "❌ Owner role not found."
        )

        return

    if owner_role not in ctx.author.roles:

        await ctx.send(
            "❌ Only members with the **Owner** role can use this command."
        )

        return

    # --------------------------------------------------------
    # CHECK STATUS
    # --------------------------------------------------------

    if not vouch_running:

        await ctx.send(
            "⚠️ The automatic system isn't running."
        )

        return

    # --------------------------------------------------------
    # STOP
    # --------------------------------------------------------

    vouch_running = False

    if vouch_task:

        vouch_task.cancel()

        vouch_task = None

    await ctx.send(
        "🔴 **Automatic Trade Activity Stopped**"
    )


# ============================================================
# STATUS
# OWNER ROLE ONLY
# ============================================================

@bot.command(
    name="vouchstatus"
)
async def vouch_status(ctx):

    # --------------------------------------------------------
    # CHECK OWNER ROLE
    # --------------------------------------------------------

    owner_role = ctx.guild.get_role(
        OWNER_ROLE_ID
    )

    if owner_role is None:

        await ctx.send(
            "❌ Owner role not found."
        )

        return

    if owner_role not in ctx.author.roles:

        await ctx.send(
            "❌ Only members with the **Owner** role can use this command."
        )

        return

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    if vouch_running:

        await ctx.send(
            "🟢 **Status:** Running\n"
            "⏱️ **Interval:** 10 minutes\n"
            "🔄 **Middleman:** Alternating\n"
            f"📸 **Vouch Photos:** {len(VOUCH_PHOTOS)}"
        )

    else:

        await ctx.send(
            "🔴 **Status:** Stopped"
        )


# ============================================================
# ADD PERMANENT VOUCH PICTURE
# OWNER ROLE ONLY
# ============================================================

@bot.command(
    name="vouchpic"
)
async def vouchpic(ctx):

    # --------------------------------------------------------
    # CHECK OWNER ROLE
    # --------------------------------------------------------

    owner_role = ctx.guild.get_role(
        OWNER_ROLE_ID
    )

    if owner_role is None:

        await ctx.send(
            "❌ Owner role not found."
        )

        return

    if owner_role not in ctx.author.roles:

        await ctx.send(
            "❌ Only members with the **Owner** role can use this command."
        )

        return

    # --------------------------------------------------------
    # CHECK ATTACHMENT
    # --------------------------------------------------------

    if not ctx.message.attachments:

        await ctx.send(
            "❌ Please attach a picture.\n"
            "Example: `$vouchpic` and attach the picture."
        )

        return

    attachment = ctx.message.attachments[0]

    # --------------------------------------------------------
    # CHECK IMAGE
    # --------------------------------------------------------

    if (
        not attachment.content_type
        or not attachment.content_type.startswith("image/")
    ):

        await ctx.send(
            "❌ The attachment must be an image."
        )

        return

    # --------------------------------------------------------
    # PREVENT DUPLICATES
    # --------------------------------------------------------

    if attachment.url in VOUCH_PHOTOS:

        await ctx.send(
            "⚠️ That picture is already in the vouch picture list."
        )

        return

    # --------------------------------------------------------
    # ADD PHOTO
    # --------------------------------------------------------

    VOUCH_PHOTOS.append(
        attachment.url
    )

    # --------------------------------------------------------
    # SAVE PERMANENTLY
    # --------------------------------------------------------

    save_vouch_photos()

    # --------------------------------------------------------
    # CONFIRM
    # --------------------------------------------------------

    await ctx.send(
        "✅ **Vouch picture added!**\n"
        f"📸 Total vouch pictures: **{len(VOUCH_PHOTOS)}**\n"
        "💾 The picture has been permanently saved."
    )

    print(
        f"Vouch picture added by {ctx.author}: "
        f"{attachment.url}"
    )


# ============================================================
# ERROR HANDLER
# ============================================================

@bot.event
async def on_command_error(
    ctx,
    error
):

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
