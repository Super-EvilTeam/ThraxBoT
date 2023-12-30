import discord
from UI.select_menu import SelectMenu
from build_finder import load_json


text_data = load_json('Text_data.json')
ui_text = load_json('UI_text.json')

class SelectLanguage(discord.ui.View):
  def __init__(self,user_id):
    super().__init__()
    self.user_id = user_id

  def button_click(self,label):
    embed = discord.Embed(colour=0xC934EB,title='Build Finder',description=ui_text[label]["createBuild"])
    view = SelectMenu(embed,label,self.user_id)
    return embed,view

  @discord.ui.button(label='English',style=discord.ButtonStyle.primary)
  async def English(self,interaction: discord.Interaction, button: discord.ui.Button):
    embed,view = self.button_click(button.label.lower())
    await interaction.response.edit_message(embed=embed, view=view)

  @discord.ui.button(label='Spanish',style=discord.ButtonStyle.primary)
  async def Spanish(self,interaction: discord.Interaction, button: discord.ui.Button):
    embed,view = self.button_click(button.label.lower())
    await interaction.response.edit_message(embed=embed, view=view)

  @discord.ui.button(label='German',style=discord.ButtonStyle.primary)
  async def German(self,interaction: discord.Interaction, button: discord.ui.Button):
    embed,view = self.button_click(button.label.lower())
    await interaction.response.edit_message(embed=embed, view=view)