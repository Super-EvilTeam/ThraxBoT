import discord
import json
from  build_finder import *

def load_json(filename):
  with open(filename, 'r') as file:
      data = json.load(file)
      return data
  
text_data = load_json('src\\json\\Text_data.json')
ui_text = load_json('src\\json\\UI_text.json')

class PostBuild(discord.ui.View):
  def __init__(self,build_icon_names,img_perks,Build,total_combinations,language):
    super().__init__()
    self.language = language
    self.build_icon_names = build_icon_names
    self.Perks_list = img_perks
    self.img_perks=img_perks
    self.Build=Build
    self.total_combinations = total_combinations
    self.index = 1
    self.children[3].disabled = True
    self.first_prev = False
    self.first_next = False

  def button_click(self,button_index,to_language):
    for i in range(3):
      self.children[i].style = discord.ButtonStyle.success if i == button_index else discord.ButtonStyle.secondary
    self.img_perks = translate_to_english(self.Perks_list,self.language,to_language)
    img_generator(self.build_icon_names,self.img_perks,self.Build,self.index-1)



  @discord.ui.button(label="English", style=discord.ButtonStyle.secondary ,row=0)
  async def english(self, interaction: discord.Interaction, button: discord.ui.Button):
    self.button_click(self.children.index(button),button.label.lower())
    await interaction.response.edit_message(view=self,attachments=[discord.File("build_img.png")])

  @discord.ui.button(label="Spanish", style=discord.ButtonStyle.secondary,row=0)
  async def spanish(self, interaction: discord.Interaction, button: discord.ui.Button):
    self.button_click(self.children.index(button),button.label.lower())
    await interaction.response.edit_message(view=self,attachments=[discord.File("build_img.png")])

  @discord.ui.button(label="German", style=discord.ButtonStyle.secondary,row=0)
  async def german(self, interaction: discord.Interaction, button: discord.ui.Button):
    self.button_click(self.children.index(button),button.label.lower())
    await interaction.response.edit_message(view=self,attachments=[discord.File("build_img.png")])


  @discord.ui.button(label="<", style=discord.ButtonStyle.primary,row=1)
  async def previous(self, interaction: discord.Interaction,button: discord.ui.Button):
    self.children[5].disabled = False
    self.index -= 1
    img_generator(self.build_icon_names,self.img_perks,self.Build,self.index-1)
    if self.index == 1:
      self.children[3].disabled = True
    await interaction.response.edit_message(content=f"{ui_text[self.language]['totalCombinations']}: {self.index}-{self.total_combinations}", 
      view=self, attachments=[discord.File("build_img.png")])

  @discord.ui.button(label="Post Build", style=discord.ButtonStyle.success,row=1)
  async def post_build(self, interaction: discord.Interaction,button: discord.ui.Button):
    await interaction.response.send_message(file=discord.File("build_img.png"))

  @discord.ui.button(label=">", style=discord.ButtonStyle.primary,row=1)
  async def next(self, interaction: discord.Interaction,button: discord.ui.Button):
    self.children[3].disabled = False
    self.index += 1
    img_generator(self.build_icon_names,self.img_perks,self.Build,self.index-1)
    if self.index == self.total_combinations:
      self.children[5].disabled = True
    await interaction.response.edit_message(view=self, attachments=[discord.File("build_img.png")],
      content=f"{ui_text[self.language]['totalCombinations']}: {self.index}-{self.total_combinations}")