import os
import asyncio
import discord
import itertools
import re
from discord.interactions import Interaction
from UI.select_language import SelectLanguage
from discord.ext import commands,tasks
from server import keep_alive
from dotenv import load_dotenv
user_id = None
mods = None

def validate_basic_input(basic_input):
    # Define the pattern for the format "string/string/string"
    pattern = re.compile(r'^\s*\w+(\s*\w*)*/\s*\w+\s*/\s*\w+\s*$')  # This pattern assumes alphanumeric characters and underscores

    # Check if the input matches the pattern
    if pattern.match(basic_input):
        return True
    else:
        return False

class RecruitForm(discord.ui.Modal, title="Recruitment Form"):
  basic = discord.ui.TextInput(row=0,label= "IGN/Platform/Region",placeholder='eg. SuperEvilTeam/PC/SEA',required=True,style=discord.TextStyle.short)
  playtime = discord.ui.TextInput(label= "How many hours you have in game?",placeholder='eg. 100+, 500+, 1000+, 2000+',required=True,style=discord.TextStyle.short)
  Hesca = discord.ui.TextInput(label= "Can you Solo Heroic Escalation under 30 min?",placeholder='Yes/No',required=True,style=discord.TextStyle.short)
  Titles = discord.ui.TextInput(label= "Which Trials/Gauntlet Titles you have?",placeholder='eg. The Dauntless,The Gauntless, Trials Champion, Hammer Champion etc',required=False,style=discord.TextStyle.long)

  async def on_submit(self, interaction: discord.Interaction):
    # Validate the 'basic' input format
    basic_input = self.basic.value
    if not validate_basic_input(basic_input):
        # If the input is not in the proper format, send an error message to the user
        await interaction.response.send_message(f"   {self.basic.value}           <------\n\nError: Please enter the 'IGN/Platform/Region' in the correct format (e.g., SuperEvilTeam/PC/SEA).", ephemeral=True)
        return
    await interaction.response.send_message(f"Thank you for Applying to Guild {interaction.user.mention}, Officers will check it and reach out to you!",ephemeral=True)
    channel = discord.utils.get(interaction.guild.channels,name = "recruitment-applications")
    await channel.send(
      f"Application submitted by {interaction.user.mention} \n\nBasic Info: {self.basic} \nPlaytime: {self.playtime} \nHesca Under 30: {self.Hesca} \nTitles: {self.Titles}"
    )

if __name__ == '__main__':
  load_dotenv()
  my_secret = os.environ.get('TOKEN')

  bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

  @bot.event
  async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} application (/) commands.")
    except Exception as e:
        print(e)
    activities = ["It's All Shits & Giggles Until You Start Hearing Baby Arm!Baby Arm! in VC",
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


  @bot.event
  async def on_message(message):
    if message.content.startswith('!'):
      await bot.process_commands(message)
    elif all(word in message.content.lower() for word in ['how', 'to', 'join']):
      view = discord.ui.View()
      button = discord.ui.Button(label="Apply", url=os.environ['FORM'])
      view.add_item(button)
      msg ="Looking to join Guild? Apply on below link \nOfficer's will check your application and reach out to you!"
      await message.channel.send(msg, view=view)

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
          role_names = ["Scout", 'WARRIORS']  # Replace with the actual names of the roles
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

  @bot.tree.command(name="build_finder")
  async def hello(interaction: discord.Interaction):
    user_id = interaction.user.id
    embed = discord.Embed(
        colour=0xC934EB,
        title='Build Finder',
        description='Select your Language')
    view_menu = SelectLanguage(user_id)
    await interaction.response.send_message(embed=embed,view=view_menu,ephemeral=True)

  @bot.tree.command(name="join_guild")
  async def recruit(interaction: discord.Interaction):
      # Check if the member has a specific role (e.g., "Admin")
      required_role_name = "LFG"
      required_role = discord.utils.get(interaction.guild.roles, name=required_role_name)

      if required_role and required_role in interaction.user.roles:
          # The member has the required role, send the modal
          modal = RecruitForm()
          await interaction.response.send_modal(modal)
      else:
          # The member doesn't have the required role, send a message or take other action
          await interaction.response.send_message("Test feature not fully implemented yet", ephemeral=True)

  # keep_alive()
  bot.run(my_secret)