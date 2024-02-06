import os
import asyncio
import discord
from UI.SelectLanguage import SelectLanguage
from UI.RecruitForm import RecruitForm
from UI.MetaBuilds import MetaBuilds
from UI.SaveBuilds import SavedBuilds
from discord.ext import commands,tasks
from dotenv import load_dotenv
from PIL import Image,ImageFilter
from build_finder import img_generator,load_json,get_path
from Gauntlet_leaderboard import display_leaderboard
user_id = None
mods = None
message_id = None
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

if __name__ == '__main__':
    load_dotenv()
    my_secret = os.environ.get('TOKEN')
    bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
    
    @bot.event
    async def on_ready():
        print('We have logged in as {0.user}'.format(bot))
        Update_leaderboard.start()
        try:
            synced = await bot.tree.sync()
            print(f"Synced {len(synced)} application (/) commands.")
        except Exception as e:
            print(e)
        activities = ["Looking for Build? Use \meta_builds",
                    "Fetching Leaderboard......",
                    "Thraxx in Thraxx enjoyer actually means Weed not Behemoth itself!",
                    "Laughing at Void Runners"]
        while True:
            for i in range(len(activities)):
                activity = discord.CustomActivity(name=activities[i])
                await bot.change_presence(activity=activity)
                await asyncio.sleep(60*5)

    #   channel_id = 1163338804820721684
    #   channel = bot.get_channel(channel_id)
    #   await channel.send(
    #     "Guess what!\n\nIt's Time to purge some sleeping warriors into the void!\n\n*Thrax laughing noises*"
    #   )
    
    @tasks.loop(minutes=5)
    async def Update_leaderboard():
        global message_id  # Use the global variable

        url_to_request = "https://storage.googleapis.com/dauntless-gauntlet-leaderboard/production-gauntlet-season10.json?_=1707132565947"
        img = display_leaderboard(url_to_request)

        channel = discord.utils.get(bot.get_all_channels(), name=channel_name)

        if channel:
            if message_id:  # If message ID exists, edit the message
                try:
                    message = await channel.fetch_message(message_id)
                    await message.edit(attachments=[discord.File(img, 'leaderboard.png')])
                except discord.errors.NotFound:
                    # Handle if the message is not found (deleted or not sent yet)
                    message_id = None
            else:
                # Send a new message and store the message ID
                message = await channel.send(file=discord.File(img, 'leaderboard.png'))
                message_id = message.id

    @bot.event
    async def on_message(message):
        if message.content.startswith('!'):
            await bot.process_commands(message)
        if all(word in message.content.lower() for word in ['how', 'to', 'join']):
            view = discord.ui.View()
            button = discord.ui.Button(label="Apply", url=os.environ['FORM'])
            view.add_item(button)
            msg ="Looking to join Guild? Apply on below link \nOfficer's will check your application and reach out to you!"
            await message.channel.send(msg, view=view)
        if isinstance(message.channel, discord.TextChannel) and message.channel.name == "builds":
            # Check if the message contains both "give" and "build"
            if all(word in message.content.lower() for word in ['give', 'build']):
                # Reply with "Are you looking for a build?"
                await message.reply("Looking for a build? Use /meta_builds", delete_after=10)

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