import os
import asyncio
import discord
import time,re,pytz
from datetime import datetime
from UI.SelectLanguage import SelectLanguage
from UI.RecruitForm import RecruitForm
from UI.MetaBuilds import MetaBuilds
from UI.SaveBuilds import SavedBuilds
from discord.ext import commands,tasks
from dotenv import load_dotenv
from PIL import Image,ImageFilter
from build_finder import img_generator,load_json,get_path
from Gauntlet_leaderboard import display_leaderboard
from Trials_leaderboard import display_trialsleaderboard
from Group_Trialsleaderboard import display_trialsgrpleaderboard
user_id = None
mods = None
gauntletlb_msg_id = None
trialslb_msg_id = None
trialsgrplb_msg_id = None
channel_name = "📜︱leaderboard"
#discord flask pillow python-dotenv requests

def resize_and_sharpen(input_path, output_path, new_size, sharpness=2.0):
    # Open the original image
    original_image = Image.open(input_path)

    # Resize the image
    resized_image = original_image.resize(new_size, Image.BOX)

    # Sharpen the resized image with a customizable sharpness level
    sharpened_image = resized_image.filter(ImageFilter.UnsharpMask(radius=2, percent=10))

    # Save the sharpened image to the output path
    sharpened_image.save(output_path)

async def SyncCommand():
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} application (/) commands.")
    except Exception as e:
        print(e)

async def SendMsg():
    channel_id = 1163338804820721684
    channel = bot.get_channel(channel_id)
    await channel.send("Guess what!\n\nIt's Time to purge some sleeping warriors into the void!\n\n*Thrax laughing noises*")

import re
import pytz  # Import the pytz library for timezone handling
from datetime import datetime

async def TimeFormat(message):
    if message.author == bot.user:
        return

    # Regular expression to match times like 12 pm, 12:30 am or 12 am
    time_pattern = r'(\d{1,2})(?::(\d{2}))?\s?(am|pm)'
    matches = re.findall(time_pattern, message.content.lower())
    
    replaced_message = message.content  # Initialize with the original message
    
    if matches:
        for match in matches:
            # Access the timestamp of the message in UTC
            timestamp_utc = message.created_at
            # Get the user's timezone
            user_timezone = pytz.timezone('YOUR_USER_TIMEZONE')  # Replace with the user's timezone
            # Convert the timestamp to the user's timezone
            timestamp_user_timezone = timestamp_utc.astimezone(user_timezone)
            # Print the timestamp
            print(f"Message sent at: {timestamp_user_timezone}")
            hour_str = match[0]
            minute_str = match[1] if match[1] else '00'
            time_str = f"{hour_str}:{minute_str}"
            # Construct the time string including the user's local timezone
            full_time_str = f"{time_str} {match[2]} {datetime.now().strftime('%m/%d/%Y')}"
            try:
                time_obj = datetime.strptime(full_time_str, '%I:%M %p %m/%d/%Y')
                # Get the user's timezone
                user_timezone = pytz.timezone('Asia/Kolkata')  # Replace 'YOUR_USERS_TIMEZONE' with the user's actual timezone
                # Convert the time object to the user's timezone
                time_obj = time_obj.astimezone(user_timezone)
                unix_timestamp = int(time_obj.timestamp())
                
                # Replace the time mentioned in the message with its Unix timestamp
                replaced_message = re.sub(time_pattern, f"<t:{unix_timestamp}:t>", replaced_message, count=1)
            except ValueError:
                pass  # Ignore if the time format is invalid
        author_name = message.author.nick if message.author.nick else message.author.name
        await message.channel.send(f"{author_name} said {replaced_message}")

async def CheckJoin(message):
    if message.author == bot.user:
        return
    if message.channel.name == 'recruitment':  # Check if the message is sent in the 'recruitment' channel
            if all(word in message.content.lower() for word in ['how', 'to', 'join']):
                view = discord.ui.View()
                button = discord.ui.Button(label="Apply", url=os.environ['FORM'])
                view.add_item(button)
                msg = "Looking to join Guild? Apply on below link \nOfficers will check your application and reach out to you!"
                await message.channel.send(msg, view=view)

async def CheckBuild(message):
    if message.author == bot.user:
        return
    if isinstance(message.channel, discord.TextChannel) and message.channel.name == "builds":
        # Check if the message contains both "give" and "build"
        if all(word in message.content.lower() for word in ['give', 'build']):
            # Reply with "Are you looking for a build?"
            await message.reply("Looking for a build? Use /meta_builds", delete_after=10)

activities = ["Looking for Build? Use \meta_builds",
              "Fetching Leaderboard......",
              "Thraxx in Thraxx enjoyer actually means Weed not Behemoth itself!",
              "Laughing at Void Runners"]

if __name__ == '__main__':
    load_dotenv()
    my_secret = os.environ.get('TOKEN')
    bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
    
    @bot.event
    async def on_ready():
        print('We have logged in as {0.user}'.format(bot))
        # await SyncCommand()
        try:
            Update_leaderboard.start()
            change_activities.start()
        except Exception as e:
            print(e)
                   
    @tasks.loop(seconds=60*4)
    async def change_activities():
        for activity_text in activities:
            activity = discord.CustomActivity(name=activity_text)
            await bot.change_presence(activity=activity)
            await asyncio.sleep(60)  # Ensure smooth transition between activities
    
    @tasks.loop(seconds=60)
    async def Update_leaderboard():
        global gauntletlb_msg_id
        global trialslb_msg_id
        global trialsgrplb_msg_id

        url_to_request = "https://storage.googleapis.com/dauntless-gauntlet-leaderboard/production-gauntlet-season11.json"
        img = display_leaderboard(url_to_request)
        week = "58"
        trials_lb_img = display_trialsleaderboard(week)
        trialsgrp_lb_img = display_trialsgrpleaderboard(week)

        channel = discord.utils.get(bot.get_all_channels(), name=channel_name)

        if channel:
            try:
                if gauntletlb_msg_id and trialslb_msg_id and trialsgrplb_msg_id:  # If message ID exists, edit the message
                    try:
                        message1 = await channel.fetch_message(gauntletlb_msg_id)
                        message2 = await channel.fetch_message(trialslb_msg_id)
                        message3 = await channel.fetch_message(trialsgrplb_msg_id)
                        await message1.edit(content=f"`Last updated on:`<t:{int(time.time())}:t>",attachments=[discord.File(img, 'leaderboard.png')])
                        await message2.edit(content=f"`Last updated on:`<t:{int(time.time())}:t>",attachments=[discord.File(trials_lb_img, 'trials_leaderboard.png')])
                        await message3.edit(content=f"`Last updated on:`<t:{int(time.time())}:t>",attachments=[discord.File(trialsgrp_lb_img, 'trials_leaderboard.png')])
                    except discord.errors.NotFound:
                        # Handle if the message is not found (deleted or not sent yet)
                        gauntletlb_msg_id = None
                        trialslb_msg_id = None
                        trialsgrplb_msg_id = None
                else:
                    # Send a new message and store the message ID
                    message1 = await channel.send(content=f"`Last updated on:`<t:{int(time.time())}:t>", file=discord.File(img, 'leaderboard.png'))
                    message2 = await channel.send(content=f"`Last updated on:`<t:{int(time.time())}:t>",file=discord.File(trials_lb_img, 'trials_leaderboard.png'))
                    message3 = await channel.send(content=f"`Last updated on:`<t:{int(time.time())}:t>",file=discord.File(trialsgrp_lb_img, 'trials_leaderboard.png'))
                    gauntletlb_msg_id = message1.id
                    trialslb_msg_id = message2.id
                    trialsgrplb_msg_id =message3.id
            except Exception as e:
                pass
                # Handle any other exceptions raised within the loop
                # message = await channel.fetch_message(message_id)
                # await message.edit(content=f" <:pepe_sad:1065643497035661422> \n Bruh I am getting rate limited when it pass away I will update!")
                # print(f"An error occurred: {e}")

    @bot.event
    async def on_message(message):
        # await TimeFormat(message)
        await CheckJoin(message)
        await CheckBuild(message)

    @bot.event
    async def on_message_delete(message):
        # Check if the deleted message is from the "guild_members" channel
        if message.channel.name == 'guild-members':
            mentioned_members = message.mentions

            for member in mentioned_members:
                # Assuming 'Scout' and 'Warrior' are the role names you want to remove
                scout_role = discord.utils.get(message.guild.roles, name='Scout')
                warrior_role = discord.utils.get(message.guild.roles, name='WARRIORS')

                if scout_role and warrior_role:
                    # Remove roles from the mentioned member
                    await member.remove_roles(scout_role, warrior_role)
                    print(f'Removed roles from {member.display_name}: Scout, WARRIORS')
                    
    @bot.event
    async def on_reaction_add(reaction, user):
        # Check if the reaction is a tick mark emoji and if the message is in the 'recruitment-application' channel
        if str(reaction.emoji) == '✅' and reaction.message.channel.name == 'recruitment-applications':
            role_names = ["Scout", 'Warriors']  # Replace with the actual names of the roles
            roles = [discord.utils.get(reaction.message.guild.roles, name=role_name) for role_name in role_names]

            if all(roles):  # Check if all roles are found
                # Get the user mentioned in the message
                mentioned_user = reaction.message.mentions[0] if reaction.message.mentions else None
                if mentioned_user and not any(role in mentioned_user.roles for role in roles):
                    # Check if the user doesn't already have any of the roles
                    await mentioned_user.add_roles(*roles)

                    # Extract the IGN (In-Game Name) from the message content
                    content = reaction.message.content
                    ign_start = content.find("Basic Info:") + len("Basic Info:")
                    ign_end = content.find("/", ign_start)
                    ign = content[ign_start:ign_end].strip()

                    # Set the nickname for the mentioned user
                    await mentioned_user.edit(nick=ign)

                    await reaction.message.channel.send(f'{mentioned_user.mention} has been invited to the guild by {user.mention}')

                    # Send a message in the 'recruitment' channel
                    recruitment_channel = discord.utils.get(reaction.message.guild.channels, name='recruitment')
                    if recruitment_channel:
                        congrats_emoji = '🎉'
                        welcome_message = f'\n {congrats_emoji} Welcome to Guild {mentioned_user.mention}! {congrats_emoji}\n\nYour application has been verified, and a Guild invite has been sent to you by {user.mention}'
                        await recruitment_channel.send(welcome_message)
                    else:
                        print("Recruitment channel not found.")

                    # Send a message in the 'guild-members' channel
                    guild_members_channel = discord.utils.get(reaction.message.guild.channels, name='guild-members')
                    if guild_members_channel:
                        await guild_members_channel.send(f'{mentioned_user.mention}')
                    else:
                        print("Guild Members channel not found.")

    @bot.tree.command(name="build-finder",description="create builds by simply selecting the perks you want")
    async def build_finder(interaction: discord.Interaction):
        embed = discord.Embed(
            colour=0xC934EB,
            title='Build Finder',
            description='Select your Language')
        view_menu = SelectLanguage(user_id)
        await interaction.response.send_message(embed=embed,view=view_menu,ephemeral=True)

    @bot.tree.command(name="join-guild",description="Send an application to join Guild")
    async def recruit(interaction: discord.Interaction):
        # Check if the member has a specific role (e.g., "Admin")
        required_role_name = "Guest"
        required_role = discord.utils.get(interaction.guild.roles, name=required_role_name)

        if required_role and required_role in interaction.user.roles:
            # The member has the required role, send the modal
            modal = RecruitForm()
            await interaction.response.send_modal(modal)
        else:
            # The member doesn't have the required role, send a message or take other action
            await interaction.response.send_message("Only Guest members can apply to guild.", ephemeral=True)

    @bot.tree.command(name="meta-builds",description="General Meta builds for all Hunts")
    async def meta_builds(interaction: discord.Interaction):
        view_menu = MetaBuilds()
        await interaction.response.send_message(file=discord.File(get_path("AllWeapons.png")),view=view_menu,ephemeral=True)

    @bot.tree.command(name="saved-builds",description="View your saved builds")
    async def s_b(interaction: discord.Interaction):
        user_id = str(interaction.user.id)
        saved_builds = load_json("saved_builds.json")
        if user_id not in saved_builds:
            await interaction.response.send_message("You dont have any saved builds",ephemeral=True)
        else:
            view_menu = SavedBuilds(interaction.user.id)
            await interaction.response.send_message(view=view_menu,ephemeral=True)

    bot.run(my_secret)