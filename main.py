import os
import discord
from UI.select_language import SelectLanguage
from discord.ext import commands
from server import keep_alive
from dotenv import load_dotenv

user_id = None
mods = None

# class Recruitment(discord.ui.View):
#   def __init__(self):
#     super().__init__()

#   reply_message = "Are you looking to join? Fill out the form!"
#   embed = discord.Embed(description=reply_message, color=0x7289DA)
#   button = discord.ui.Button(label="Click me!", url="https://www.example.com")
#   # Create an action row and add the button to it
#   action_row = discord.ui.ActionRow()
#   action_row.add_button(button)


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
    activity = discord.CustomActivity(name='Laughing at Void Runners')
    await bot.change_presence(activity=activity)
    # channel_id = 1163338804820721684
    # channel = bot.get_channel(channel_id)
    # await channel.send("<:devastated:1065643480879222846>")

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


  @bot.tree.command(name="build_finder")
  async def hello(interaction: discord.Interaction):
    user_id = interaction.user.id
    embed = discord.Embed(
        colour=0xC934EB,
        title='Build Finder',
        description='Select your Language')
    view_menu = SelectLanguage(user_id)
    await interaction.response.send_message(embed=embed,view=view_menu,ephemeral=True)

  # @bot.tree.command(name="recruit")
  # async def recruit(interaction: discord.Interaction):
  #   Username = interaction.user.name
  #   modal = RecruitForm(Username)
  #   await interaction.response.send_modal(modal)

  keep_alive()
  bot.run(my_secret)