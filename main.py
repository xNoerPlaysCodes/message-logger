import discord, json, datetime
from config import TOKEN, PREFIX, owner

intents = discord.Intents.default()
intents.message_content = True  # Allows the bot to receive message events
client = discord.Client(intents=intents)

helpMenu = f"""
{PREFIX}log_start <channel id> - Starts the logging in specified channel id.
{PREFIX}log_stop - Stops logging if enabled.
"""

def isBot(user):
    return user.bot

@client.event
async def on_ready():
    await client.change_presence(activity=discord.Game(name=f"{PREFIX}help"))
    print("Bot is ready.")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if isBot(message.author):
        return

    if message.content == f"{PREFIX}log_start":
        if message.author.guild_permissions.manage_messages:
            try:
                with open("log_channel.json", "r") as f:
                    server_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                server_data = []

            server_id = str(message.guild.id)
            server_entry = next((data for data in server_data if data['server_id'] == server_id), None)

            if not server_entry:
                server_data.append({"server_id": server_id, "log_enabled": True, "log_channel": int(message.channel.id)})

                with open("log_channel.json", "w") as f:
                    json.dump(server_data, f, indent=4)

                await message.channel.send("Logging enabled for this server and channel.")
            else:
                await message.channel.send("Logging is already enabled for this server and channel.")

    elif message.content == f"{PREFIX}log_stop":
        if message.author.guild_permissions.manage_messages:
            try:
                with open("log_channel.json", "r") as f:
                    server_data = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError):
                server_data = []

            server_id = str(message.guild.id)
            server_entry = next((data for data in server_data if data['server_id'] == server_id), None)

            if server_entry:
                server_entry["log_enabled"] = False

                with open("log_channel.json", "w") as f:
                    json.dump(server_data, f, indent=4)

                await message.channel.send("Logging disabled for this server.")
            else:
                await message.channel.send(f"Server logging was not enabled using {PREFIX}log_start.")

    elif message.content == f"{PREFIX}help":
        embed = discord.Embed(
            title="Help Menu",
            description=helpMenu,
            color=discord.Color(int("FFFFFF", 16))
        )
        embed.set_footer(text="The best message logger.")
        await message.channel.send(embed=embed)

# Load the list of server data from log_channel.json if the file exists
try:
    with open("log_channel.json", "r") as f:
        server_data = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    server_data = []

@client.event
async def on_message_delete(message):
    if message.author == client.user:
        return
    if isBot(message.author):
        return

    try:
        with open("log_channel.json", "r") as f:
            server_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        server_data = []

    server_id = str(message.guild.id)
    server_entry = next((data for data in server_data if data['server_id'] == server_id), None)

    if server_entry and server_entry["log_enabled"]:
        log_channel_id = server_entry.get("log_channel")
        if log_channel_id:
            log_channel = message.guild.get_channel(log_channel_id)
            if log_channel:
                time_now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                embed = discord.Embed(
                    title=f"{message.author.name} deleted",
                    description=message.content,
                    color=discord.Color(int("FFFFFF", 16)),
                )
                embed.set_footer(text=f"Deleted at {time_now}")
                await log_channel.send(embed=embed)

@client.event
async def on_message_edit(before, after):
    if before.author == client.user:
        return
    if isBot(before.author):
        return

    try:
        with open("log_channel.json", "r") as f:
            server_data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        server_data = []

    server_id = str(before.guild.id)
    server_entry = next((data for data in server_data if data['server_id'] == server_id), None)

    if server_entry and server_entry["log_enabled"]:
        log_channel_id = server_entry.get("log_channel")
        if log_channel_id:
            log_channel = before.guild.get_channel(log_channel_id)
            if log_channel:
                time_now = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
                embed = discord.Embed(
                    title=f"{before.author.name} edited",
                    description=f"Original Message:\n{before.content}\nNew Message:\n{after.content}",
                    color=discord.Color(int("FFFFFF", 16)),
                )
                embed.set_footer(text=f"Edited at {time_now}")
                await log_channel.send(embed=embed)

# Load the list of server data from log_channel.json if the file exists
try:
    with open("log_channel.json", "r") as f:
        server_data = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    server_data = []

client.run(TOKEN)
