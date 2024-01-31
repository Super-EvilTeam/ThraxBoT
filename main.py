import os
import asyncio
import discord
import itertools
import json
import re
from discord.interactions import Interaction
from UI.select_language import SelectLanguage
from discord.ext import commands,tasks
from server import keep_alive
from dotenv import load_dotenv
from PIL import Image,ImageFilter
import io
from build_finder import img_generator,load_json
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

def resize_and_sharpen(input_path, output_path, new_size, sharpness=2.0):
    # Open the original image
    original_image = Image.open(input_path)

    # Resize the image
    resized_image = original_image.resize(new_size, Image.BOX)

    # Sharpen the resized image with a customizable sharpness level
    sharpened_image = resized_image.filter(ImageFilter.UnsharpMask(radius=2, percent=10))

    # Save the sharpened image to the output path
    sharpened_image.save(output_path)

weapon_emoji =['<:as:1192842658343817226>',
        '<:axe:1192852193229934663>',
        '<:cb:1192850297563914271>',
        '<:hammer:1192852188767195237>',
        '<:repeater:1192852181683019907>',
        '<:sword:1192846249804697692>',
        '<:pike:1192852184245751808>']

element_emoji = ["<:frost:1192869317251956886>",
                "<:blaze:1192869335987925202>",
                "<:shock:1192868564227596440>",
                "<:terra:1192869323841208461>",
                "<:umbral:1192869332225622166>",
                "<:radiant:1192869315251294301>"]

omnicell_emoji = ["<:RevenantAbility:1174970642316136528>",
                "<:DisciplineAbility:1174970622812631041>",
                "<:BastionAbility:1174970614000390216>",
                "<:TempestAbility:1174970651656847450>",
                "<:ArtificerAbility:1174970606605840444>",
                "<:IceborneAbility:1174970634242105364>"]

meta_builds_data = load_json("Meta_builds.json")


def generate_options(option_list,emoji=False):
    if emoji:
        options = [discord.SelectOption(label=weapon,value=weapon, emoji=emoji[index]) for index, weapon in enumerate(option_list)]
    else:
       options = [discord.SelectOption(label=weapon,value=weapon) for index, weapon in enumerate(option_list)]
    return options

weapons = ["Aether Strikers", "Axe", "Chain Blades", "Hammer", "Repeater", "Sword", "War Pike"]
omnicell = ["Revenant", "Discipline", "Bastion", "Tempest", "Artificer", "Iceborne"]
element = ["Frost","Blaze","Shock","Terra","Umbral","Radiant"]


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

class MetaBuilds(discord.ui.View):
    def __init__(self):
        super().__init__()
        # self.embed = embed
        self.selected_weapon = None
        self.selected_omnicell = None
        self.selected_element = None
        self.SelectWeapon.options=generate_options(weapons,weapon_emoji)
        self.SelectOmnicell.options = generate_options(omnicell,omnicell_emoji)
        self.SelectElement.options = generate_options(element,element_emoji)

    async def callback(self,select,interaction):
       for i in select.options:
          if i.default == True:
             i.default = False
          if i.label == select.values[0]:
             i.default = True
       print(select.options[0].default)
       print(self.selected_weapon)
       if self.selected_element != None and self.selected_omnicell != None and self.selected_weapon != None:
        data = meta_builds_data[self.selected_weapon][self.selected_omnicell][self.selected_element]
        img = img_generator([data["Icon"]],data["Perks"],0,0)
        await interaction.response.edit_message(attachments=[discord.File(img, filename='image.png')],view = self)
        return True
       return False

    @discord.ui.select(placeholder="Select Weapon")
    async def SelectWeapon(self, interaction, select):
       self.selected_weapon = select.values[0]
       if not await self.callback(select,interaction):
          await interaction.response.defer()

    @discord.ui.select(placeholder="Select Omnicell")
    async def SelectOmnicell(self, interaction, select):
       self.selected_omnicell = select.values[0]
       print(self.selected_omnicell)
       if not await self.callback(select,interaction):
          await interaction.response.defer()
    
    @discord.ui.select(placeholder="Select Element")
    async def SelectElement(self, interaction, select):
       self.selected_element = select.values[0]
       print(self.selected_element)
       if not await self.callback(select,interaction):
          await interaction.response.defer()

class SavedBuilds(discord.ui.View):
   def __init__(self,user_id):
        super().__init__()
        self.saved_builds = load_json("saved_builds.json")
        self.user_id = str(user_id)
        self.saved_build.options=generate_options(list(self.saved_builds[str(self.user_id)].keys()))
        self.Icons = None
        self.Perks = None
        self.post_build.disabled = True

   @discord.ui.select(placeholder="Select Saved Build")
   async def saved_build(self, interaction, select):
      self.Icons = self.saved_builds[self.user_id][select.values[0]]["Icons"]
      self.Perks = self.saved_builds[self.user_id][select.values[0]]["Perks"]
      self.img = img_generator([self.Icons],self.Perks,0,0)
      self.post_build.disabled = False
      self.post_build.style = discord.ButtonStyle.success
      await interaction.response.edit_message(attachments=[discord.File(self.img, filename='image.png')],view = self)
   
   @discord.ui.button(label="Post Build")
   async def post_build(self,interaction,button):
      self.img = img_generator([self.Icons],self.Perks,0,0)
      await interaction.channel.send(file=discord.File(self.img, filename='image.png'))
      await interaction.response.defer()
      
if __name__ == '__main__':
  load_dotenv()
  my_secret = os.environ.get('TOKEN')
  bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())

  @bot.tree.command(name="saved-builds",description="View your saved builds")
  async def s_b(interaction: discord.Interaction):
     user_id = str(interaction.user.id)
     saved_builds = load_json("saved_builds.json")
     if user_id not in saved_builds:
        await interaction.response.send_message("You dont have any saved builds",ephemeral=True)
     view_menu = SavedBuilds(interaction.user.id)
     await interaction.response.send_message(view=view_menu,ephemeral=True)
  
  @bot.event
  async def on_ready():
    print('We have logged in as {0.user}'.format(bot))
    
    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} application (/) commands.")
    except Exception as e:
        print(e)
    activities = ["Looking for Build? Use \meta_builds",
                  "It's All Shits & Giggles Until You Start Hearing Baby Arm!Baby Arm! in VC",
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

  # keep_alive()
  bot.run(my_secret)