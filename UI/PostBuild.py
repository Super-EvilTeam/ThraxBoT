import discord
from  build_finder import *
# from UI.MetaBuilds import generate_options

mods_data = load_json('Mods&Specials.json')
ui_text = load_json('UI_text.json')


def generate_options(option_list,emoji=False):
    if emoji:
        options = [discord.SelectOption(label=weapon,value=weapon, emoji=emoji[index]) for index, weapon in enumerate(option_list)]
    else:
       options = [discord.SelectOption(label=weapon,value=weapon) for index, weapon in enumerate(option_list)]
    return options

class BuildName(discord.ui.Modal, title="Save Build"):
  def __init__(self, build_icon_names, image_perks, index,mod,special,tonics):
      super().__init__()
      self.build_icon_names = build_icon_names
      self.index = index
      self.image_perks = image_perks
      self.mod = mod
      self.special = special
      self.tonics = tonics

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
          "Perks": self.image_perks,
          "Mod": self.mod,
          "Special":self.special,
          "Tonics": self.tonics
      }

      # Save the updated data back to the JSON file
      with open(get_path('saved_builds.json'), 'w') as file:
          json.dump(saved_builds, file, indent=4)

      # You can also send a confirmation message if needed
      await interaction.response.send_message(f"Build saved", ephemeral=True)

class ShareBuild(discord.ui.View):
  def __init__(self,build_icon_names,img_perks,Build,total_combinations,language,weapon_type):
    super().__init__()
    self.weapon_type = weapon_type
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
    self.mod_img = None
    self.wspecial_img = None
    self.tonics = None
    self.select_mods.options = generate_options(mods_data[weapon_type]["Mods"])
    self.select_wspecial.options = generate_options(mods_data[weapon_type]["Specials"])
    self.set_tonics.options = generate_options(["Blitz Tonic","Frenzy Tonic","Aetherdrive Tonic","AssaultTonic","InspiringPylon"])

  def button_click(self,button_index,to_language):
    for i in range(3):
      self.children[i].style = discord.ButtonStyle.success if i == button_index else discord.ButtonStyle.secondary
    self.img_perks = translate_to_english(self.Perks_list,self.language,to_language)
    self.img = img_generator(self.build_icon_names,self.img_perks,self.Build,self.index-1)
  
  async def update_view(self,interaction,button):
    if button.custom_id==">":
      self.previous.disabled = False
      self.index += 1
    else:
      self.next.disabled = False
      self.index -= 1
    if self.index == self.total_combinations:
      self.next.disabled = True
    elif self.index == 1:
      self.previous.disabled = True
    self.img = img_generator(self.build_icon_names,self.img_perks,self.Build,self.index-1,self.mod_img,self.wspecial_img,self.tonics)
    await interaction.response.edit_message(view=self, attachments=[discord.File(self.img, filename='image.png')],content=f"{ui_text[self.language]['totalCombinations']}: {self.index}-{self.total_combinations}")
  
  # @discord.ui.button(label="English", style=discord.ButtonStyle.secondary ,row=0)
  # async def english(self, interaction: discord.Interaction, button: discord.ui.Button):
  #   self.button_click(self.children.index(button),button.label.lower())
  #   await interaction.response.edit_message(view=self,attachments=[discord.File(self.img, filename='image.png')])

  # @discord.ui.button(label="Spanish", style=discord.ButtonStyle.secondary,row=0)
  # async def spanish(self, interaction: discord.Interaction, button: discord.ui.Button):
  #   self.button_click(self.children.index(button),button.label.lower())
  #   await interaction.response.edit_message(view=self,attachments=[discord.File(self.img, filename='image.png')])

  # @discord.ui.button(label="German", style=discord.ButtonStyle.secondary,row=0)
  # async def german(self, interaction: discord.Interaction, button: discord.ui.Button):
  #   self.button_click(self.children.index(button),button.label.lower())
  #   await interaction.response.edit_message(view=self,attachments=[discord.File(self.img, filename='image.png')])

  @discord.ui.select(placeholder="Set Weapon Special",row=1)
  async def select_wspecial(self,interaction,select):
    self.wspecial_img = select.values[0].replace(' ', '').replace("'", '') + '.png'
    self.img = img_generator(self.build_icon_names,self.img_perks,self.Build,self.index-1,self.mod_img,self.wspecial_img,self.tonics)
    await interaction.response.edit_message(view=self,attachments =[discord.File(self.img, filename='image.png')])

  @discord.ui.select(placeholder="Set Weapon Mod",row=2)
  async def select_mods(self,interaction,select):
    self.mod_img = select.values[0].replace(' ', '').replace("'", '') + '.png'
    self.img = img_generator(self.build_icon_names,self.img_perks,self.Build,self.index-1,self.mod_img,self.wspecial_img,self.tonics)
    await interaction.response.edit_message(attachments =[discord.File(self.img, filename='image.png')])

  @discord.ui.select(placeholder="Set Tonics/pylon)",min_values=3,max_values=3,row=3)
  async def set_tonics(self,interaction,select):
    self.tonics = [value.replace(' ', '').replace("'", '') + '.png' for value in select.values]
    print(self.tonics)
    self.img = img_generator(self.build_icon_names,self.img_perks,self.Build,self.index-1,self.mod_img,self.wspecial_img,self.tonics)
    await interaction.response.edit_message(attachments =[discord.File(self.img, filename='image.png')])

  @discord.ui.button(custom_id="<",style=discord.ButtonStyle.primary,row=4,emoji= "<:prev:1203560661125308486>")
  async def previous(self, interaction: discord.Interaction,button: discord.ui.Button):
    await self.update_view(interaction,button)
    
  @discord.ui.button(label="Post Build", style=discord.ButtonStyle.success,row=4)
  async def post_build(self, interaction: discord.Interaction,button: discord.ui.Button):
    self.img = img_generator(self.build_icon_names,self.img_perks,self.Build,self.index-1,self.mod_img,self.wspecial_img,self.tonics)
    await interaction.response.send_message(file=discord.File(self.img, filename='image.png'))

  @discord.ui.button(label="Save Build", style=discord.ButtonStyle.success, row=4)
  async def save_build(self, interaction, button):
      name =await interaction.response.send_modal(BuildName(self.build_icon_names,self.img_perks,self.index,self.mod_img,self.wspecial_img,self.tonics))
      
  @discord.ui.button(custom_id=">",style=discord.ButtonStyle.primary,row=4,emoji="<:next:1203560655685419049>")
  async def next(self, interaction: discord.Interaction,button: discord.ui.Button):
    await self.update_view(interaction,button)