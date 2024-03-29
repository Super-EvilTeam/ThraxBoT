import os,json,time
import requests
import asyncio
import discord
import time
from datetime import datetime,timedelta
from UI.SelectLanguage import SelectLanguage
from UI.RecruitForm import RecruitForm
from UI.MetaBuilds import MetaBuilds
from UI.SaveBuilds import SavedBuilds
from discord.ext import commands,tasks
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from build_finder import load_json,get_path
from Gauntlet_leaderboard import getImage_gauntlet_leaderboard
from Trials_leaderboard import fetch_trials_leaderboard,getImage_group_leaderboard,getImage_solo_leaderboard

user_id = None
mods = None

prev_trials_leaderboard = None

#discord flask pillow python-dotenv requests

def convert_timestamp(timestamp):
                # Convert the timestamp to a datetime object
                dt_object = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S%z")

                # Format the datetime object as desired
                formatted_date = dt_object.strftime("%B %d %Y")
                
                return formatted_date

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
    
async def update_solo_trialsleaderboard(data,channel,Trialsleaderboard_solo_id,current_behemoth,current_rotation_time):
    print("called update solo leaderboard")
    solo_leaderboard_img = await getImage_solo_leaderboard(data,current_behemoth,current_rotation_time)

    if not channel:
        print("Channel not found")
        return
    content = f"`Last updated on:`<t:{int(time.time())}:f>"
    try:
        if Trialsleaderboard_solo_id:  
            message = await channel.fetch_message(Trialsleaderboard_solo_id)
            await message.edit(content=content, attachments=[discord.File(solo_leaderboard_img, 'Trials Solo leaderboard.png')])
        else:
            message = await channel.send(content=content, file=discord.File(solo_leaderboard_img, 'Trials Solo leaderboard.png'))
            Trialsleaderboard_solo_id= message.id
    except discord.errors.NotFound:
        print("Message not found")
    except Exception as e:
        print(f"An error occurred: {e}")   
    
async def update_group_trialsleaderboard(data,channel,trialsgrplb_msg_id,current_behemoth,current_rotation_time):
    print("called update group leaderboard")
    
    group_leaderboard_img = await getImage_group_leaderboard(data,current_behemoth,current_rotation_time)

    if not channel:
        print("Channel not found")
        return
    content = f"`Last updated on:`<t:{int(time.time())}:f>"
    try:
        if trialsgrplb_msg_id:  
            message = await channel.fetch_message(trialsgrplb_msg_id)
            await message.edit(content=content, attachments=[discord.File(group_leaderboard_img, 'Trials Group leaderboard.png')])
        else:
            message = await channel.send(content=content, file=discord.File(group_leaderboard_img, 'Trials Group leaderboard.png'))
            trialsgrplb_msg_id= message.id
    except discord.errors.NotFound:
        print("Message not found")
    except Exception as e:
        print(f"An error occurred: {e}") 

async def update_gauntlet_leaderboard(gauntlet_leaderboard_data,channel,gauntletlb_msg_id,season,timeline):
    print("called update gauntlet leaderboard")
    gauntlet_leaderboard_img = getImage_gauntlet_leaderboard(gauntlet_leaderboard_data,season,timeline)

    if not channel:
        print("Channel not found")
        return
    print(int(time.time()))
    content = f"`Last updated on:`<t:{int(time.time())}:f>"
    try:
        if gauntletlb_msg_id:  
            message = await channel.fetch_message(gauntletlb_msg_id)
            await message.edit(content=content, attachments=[discord.File(gauntlet_leaderboard_img, 'Gauntlet leaderboard.png')])
        else:
            message = await channel.send(content=content, file=discord.File(gauntlet_leaderboard_img, 'Gauntlet leaderboard.png'))
            gauntletlb_msg_id= message.id
    except discord.errors.NotFound:
        print("Message not found")
    except Exception as e:
        print(f"An error occurred: {e}") 

async def initialize_refresh_token(authorization_code):
    def get_access_token_fortnite(authorization_code):
        url = "https://account-public-service-prod.ol.epicgames.com/account/api/oauth/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            #Below is fortnitePcClient Authorization
            "Authorization": f"Basic ZWM2ODRiOGM2ODdmNDc5ZmFkZWEzY2IyYWQ4M2Y1YzY6ZTFmMzFjMjExZjI4NDEzMTg2MjYyZDM3YTEzZmM4NGQ=" 
        }
        data = {
            "grant_type": "authorization_code",
            "code": f"{authorization_code}"
        }

        response = requests.post(url, headers=headers, data=data)
        data = json.loads(response.content)
        # print("fortnite Access token")
        # print(data)
        access_token = data['access_token']
        return access_token

    def create_exchange_code(access_token):
        url = "https://account-public-service-prod.ol.epicgames.com/account/api/oauth/exchange"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        response = requests.get(url, headers=headers)
        data = json.loads(response.content)
        # print("Exchange Code")
        # print(data)
        exchange_code = data["code"]
        return exchange_code

    def get_refresh_token_dauntless(exchange_code):
        url = 'https://api.epicgames.dev/epic/oauth/v2/token'
        headers = {
            'Accept-Encoding': 'deflate, gzip',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'Authorization': 'Basic MTJjNDI3OTg2MmFiNDQ2MGEyNWMyZTlmYTUzNWZiN2U6eEZEZnN5QkhXdllXWXZGWkxodXlqamhGNFVEUEZUNms=',
            'X-Epic-Correlation-ID': 'EOS-7Xy9sxln5k6-kd-09Q8ouQ-GmEbSTmd6UmlCwuKAdQF_w',
            'User-Agent': 'EOS-SDK/1.16.0-25515828 (Windows/10.0.22621.2506.64bit) Dauntless/1.0.0',
            'X-EOS-Version': '1.16.0-25515828'
        }
        data = {
                "grant_type": "exchange_code",
                "exchange_code": f"{exchange_code}"
            }

        response = requests.post(url, headers=headers, data=data)
        data = json.loads(response.content)
        # print("Dauntless token")
        # print(data)
        refresh_token = data['refresh_token']
        return refresh_token
    
    fr_access_token = get_access_token_fortnite(authorization_code)
    exchange_code = create_exchange_code(fr_access_token)
    refresh_token = get_refresh_token_dauntless(exchange_code)
    return refresh_token

def get_trials_rotation_info():
    url = "https://playdauntless.com/trials/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    div_tag = soup.find("div", class_="trial-summary__behemoth-name")
    time_tag = soup.find("time", class_ ="medium localize")

    end_date = time_tag.text.strip()
    end_date = datetime.strptime(end_date, "%b %d")
    start_date = end_date - timedelta(days=7)
    start_date = start_date.strftime("%b %d")
    end_date = end_date.strftime("%b %d")

    current_rotation_time = f"{start_date} - {end_date}"
    current_behemoth = div_tag.text.strip()
    return current_behemoth,current_rotation_time

if __name__ == '__main__':
    load_dotenv()
    my_secret = os.environ.get('TOKEN')
    bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

    week = 61
    current_behemoth = None
    current_rotation_time = None
    season= None
    timeline = None
    gauntletlb_msg_id = None
    Trialsleaderboard_solo_id = None
    trialsgrplb_msg_id = None
    
    refresh_token = None
    session_token = None
    first_load = True

    gauntlet_leaderboard_data = None
    solo_leaderboard_data = None
    group_leaderboard_data = None

    @bot.event
    async def on_ready():
        global refresh_token,current_behemoth,current_rotation_time,trialsgrplb_msg_id,Trialsleaderboard_solo_id,gauntletlb_msg_id,season,timeline
        
        print('We have logged in as {0.user}'.format(bot))

        authorization_code = os.environ.get('authoriazation_code')
        try:
            refresh_token = await initialize_refresh_token(authorization_code)
        except Exception as e:
            print("Refresh Authorization code")

        leaderboard_channel = discord.utils.get(bot.get_all_channels(), name="📜︱leaderboard")
        leaderboard_messages_id = [message.id async for message in leaderboard_channel.history(limit=None)]
        if leaderboard_messages_id != []:
            trialsgrplb_msg_id,Trialsleaderboard_solo_id,gauntletlb_msg_id = leaderboard_messages_id
        else:
            await leaderboard_channel.send("1")
            await leaderboard_channel.send("2")
            await leaderboard_channel.send("3")
            leaderboard_messages_id = [message.id async for message in leaderboard_channel.history(limit=None)]
            trialsgrplb_msg_id,Trialsleaderboard_solo_id,gauntletlb_msg_id = leaderboard_messages_id
        # await SyncCommand()
        
        current_behemoth,current_rotation_time = get_trials_rotation_info()

        url = "https://storage.googleapis.com/dauntless-gauntlet-leaderboard/production-gauntlet-all-seasons.json"
        response = requests.get(url)
        data = response.json()
        current_season =data['active_season']
        start_date = convert_timestamp(current_season['start_at'])
        end_date = convert_timestamp(current_season['end_at'])
        season = current_season['gauntlet_id'][-2:]
        # season = f"Gauntlet Season {season}"
        timeline = f"{start_date} - {end_date}"

        try:
            refresh_session_token.start()
            Update_leaderboard.start(leaderboard_channel)
            change_activities.start()
        except Exception as e:
            print(e)
                   
    @tasks.loop(seconds=60*4)
    async def change_activities():
        for activity_text in activities:
            activity = discord.CustomActivity(name=activity_text)
            await bot.change_presence(activity=activity)
            await asyncio.sleep(60)  # Ensure smooth transition between activities
    
    @tasks.loop(hours=2)
    async def refresh_session_token():
        global refresh_token,session_token
        def refresh_dauntless_token(refresh_token):
            url = 'https://api.epicgames.dev/epic/oauth/v2/token'
            headers = {
                'Content-Type': 'application/x-www-form-urlencoded',
                'Authorization': 'Basic MTJjNDI3OTg2MmFiNDQ2MGEyNWMyZTlmYTUzNWZiN2U6eEZEZnN5QkhXdllXWXZGWkxodXlqamhGNFVEUEZUNms=',
            }
            data = {
                    "grant_type": "refresh_token",
                    "refresh_token": f"{refresh_token}"
                }

            response = requests.post(url, headers=headers, data=data)
            data = json.loads(response.content)
            # print("Refreshed token")
            # print(data)
            access_token = data['access_token']
            refresh_token = data["refresh_token"]
            return access_token,refresh_token

        def get_session_token(access_token):
            url = 'https://gamesession-prod.steelyard.ca/gamesession/epiceos'
            headers = {
                'Accept': '*/*',
                'Accept-Encoding': 'deflate, gzip',
                'Authorization': f'BEARER {access_token}',
                'Content-Type': 'application/json; charset=utf-8',
                'X-Archon-Console': '(Windows)',
                'User-Agent': 'Archon/++dauntless+rel-1.14.6-CL-615145 Windows/10.0.22621.1.768.64bit'
            }

            response = requests.put(url, headers=headers)
            data = json.loads(response.content)
            # print("Session Token")
            # print(data)
            session_token = data["payload"]["sessiontoken"]
            return session_token
        
        # print("\n\nrefresh_token_before\n\n",refresh_token)
        access_token,refresh_token = refresh_dauntless_token(refresh_token)
        # print("\n\nrefresh_token_after\n\n",refresh_token)
        session_token = get_session_token(access_token)
        # print("\n\nsession token is below\n",session_token)
            
    @tasks.loop(seconds=10)
    async def Update_leaderboard(leaderboard_channel):
        global group_leaderboard_data,solo_leaderboard_data,gauntlet_leaderboard_data,session_token,week,current_behemoth,current_rotation_time,season,timeline
        
        response = requests.get(f"https://storage.googleapis.com/dauntless-gauntlet-leaderboard/production-gauntlet-season11.json")
        data = response.json()
        data = data["leaderboard"][:5]
        if data != gauntlet_leaderboard_data:
            gauntlet_leaderboard_data = data
            await update_gauntlet_leaderboard(gauntlet_leaderboard_data,leaderboard_channel,gauntletlb_msg_id,season,timeline)

        trials_leaderboard = await fetch_trials_leaderboard(week,session_token)
        group_data = trials_leaderboard["payload"]["world"]["group"]["entries"][:5]
        solo_data = trials_leaderboard["payload"]["world"]["solo"]["all"]["entries"][:5]

        if group_data != group_leaderboard_data:
            group_leaderboard_data = group_data
            await update_group_trialsleaderboard(group_leaderboard_data,leaderboard_channel,trialsgrplb_msg_id,current_behemoth,current_rotation_time)

        if solo_data != solo_leaderboard_data:
            solo_leaderboard_data = solo_data
            await update_solo_trialsleaderboard(solo_leaderboard_data,leaderboard_channel,Trialsleaderboard_solo_id,current_behemoth,current_rotation_time)

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