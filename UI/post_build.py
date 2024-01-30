import discord
from  build_finder import *
import base64

text_data = load_json('Text_data.json')
ui_text = load_json('UI_text.json')


class BuildName(discord.ui.Modal, title="buildname"):
  def __init__(self, build_icon_names, image_perks, index):
      super().__init__()
      self.build_icon_names = build_icon_names
      self.index = index
      self.image_perks = image_perks

  basic = discord.ui.TextInput(label="build name", style=discord.TextStyle.short)

  async def on_submit(self, interaction: discord.Interaction):
      # Load existing data from the JSON file
      saved_builds = load_json("saved_builds.json")

      # Validate the 'basic' input format
      buildname = self.basic.value

      # Check if the user has any saved builds
      user_id = str(interaction.user.id)
      # print(saved_builds)
      if user_id not in saved_builds:
          saved_builds[user_id] = {}

      # Update or create the entry for the user
      saved_builds[user_id][buildname] = {
          "Icons": self.build_icon_names[self.index - 1],
          "Perks": self.image_perks
      }

      # Save the updated data back to the JSON file
      with open('saved_builds.json', 'w') as file:
          json.dump(saved_builds, file, indent=4)

      # You can also send a confirmation message if needed
      await interaction.response.send_message(f"Build saved", ephemeral=True)

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
    self.img = None

  def button_click(self,button_index,to_language):
    for i in range(3):
      self.children[i].style = discord.ButtonStyle.success if i == button_index else discord.ButtonStyle.secondary
    self.img_perks = translate_to_english(self.Perks_list,self.language,to_language)
    self.img = img_generator(self.build_icon_names,self.img_perks,self.Build,self.index-1)
  
  async def update_view(self,interaction,button):
    if button.label==">":
      self.previous.disabled = False
      self.index += 1
    else:
      self.next.disabled = False
      self.index -= 1
    if self.index == self.total_combinations:
      self.next.disabled = True
    elif self.index == 1:
      self.previous.disabled = True
    self.img = img_generator(self.build_icon_names,self.img_perks,self.Build,self.index-1)
    await interaction.response.edit_message(view=self, attachments=[discord.File(self.img, filename='image.png')],content=f"{ui_text[self.language]['totalCombinations']}: {self.index}-{self.total_combinations}")
  
  @discord.ui.button(label="English", style=discord.ButtonStyle.secondary ,row=0)
  async def english(self, interaction: discord.Interaction, button: discord.ui.Button):
    self.button_click(self.children.index(button),button.label.lower())
    await interaction.response.edit_message(view=self,attachments=[discord.File(self.img, filename='image.png')])

  @discord.ui.button(label="Spanish", style=discord.ButtonStyle.secondary,row=0)
  async def spanish(self, interaction: discord.Interaction, button: discord.ui.Button):
    self.button_click(self.children.index(button),button.label.lower())
    await interaction.response.edit_message(view=self,attachments=[discord.File(self.img, filename='image.png')])

  @discord.ui.button(label="German", style=discord.ButtonStyle.secondary,row=0)
  async def german(self, interaction: discord.Interaction, button: discord.ui.Button):
    self.button_click(self.children.index(button),button.label.lower())
    await interaction.response.edit_message(view=self,attachments=[discord.File(self.img, filename='image.png')])


  @discord.ui.button(label="<", style=discord.ButtonStyle.primary,row=1)
  async def previous(self, interaction: discord.Interaction,button: discord.ui.Button):
    await self.update_view(interaction,button)
    
  @discord.ui.button(label="Post Build", style=discord.ButtonStyle.success,row=1)
  async def post_build(self, interaction: discord.Interaction,button: discord.ui.Button):
    img = img_generator(self.build_icon_names,self.img_perks,self.Build,self.index-1)
    await interaction.response.send_message(file=discord.File(img, filename='image.png'))

  @discord.ui.button(label="Save Build", style=discord.ButtonStyle.success, row=1)
  async def save_build(self, interaction, button):
      name =await interaction.response.send_modal(BuildName(self.build_icon_names,self.img_perks,self.index))
      
  @discord.ui.button(label=">", style=discord.ButtonStyle.primary,row=1)
  async def next(self, interaction: discord.Interaction,button: discord.ui.Button):
    await self.update_view(interaction,button)