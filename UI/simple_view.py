import discord
import json
from build_finder import *
from UI.post_build import PostBuild

text_data = load_json('Text_data.json')
ui_text = load_json('UI_text.json')


class SimpleView(discord.ui.View):

  cells_1 = ['Adrenaline', 'Berserker', 'Cascade', 'Catalyst', 'Conduit',
      'Conservation', 'Cunning', 'Endurance', 'Engineer', 'Galvanized',
      'Impulse', 'Molten', 'Overpower', 'Parasitic', 'Predator', 'Pulse',
      'Recycle', 'Reuse', 'Sharpened', 'Tenacious']

  cells_2 = ["Assassin's Frenzy", 'FleetFooted', "Invigorated", 'Fire', 'Savagery',
      'Tactician', 'Tough', 'Energized', 'Drop', 'Aetherhunter', 'Bladestorm',
      'WeightedStrikes', 'Guardian', 'Acidic', 'Aegis', 'Aetheric Attunement',
      'Medic', 'KnockoutKing', 'Rage', 'EvasiveFury']

  def __init__(self, user_id, embed, weapon_type,weapon_filter,omnicell,lantern,language):
    super().__init__()
    self.weapon = None
    self.omnicell = omnicell
    self.weapon_type = weapon_type
    self.weapon_filter = weapon_filter
    self.lantern = lantern
    self.user_id = user_id
    self.embed = embed
    self.user_counter = {}
    self.user_counter['Selected_Cells'] = []
    self.render_list = []
    self.user_counter[self.user_id] = [0] * 40 
    self.preserved_att = []
    self.preserved_att2 = []
    self.Perks_list = []
    self.language = language
    self.cells_1 = text_data["Cells_1"][language]
    self.cells_2 = text_data["Cells_2"][language]
    self.Find_Build.label = ui_text[language]["findBuild"]
    self.Reset.label = ui_text[language]["reset"]
    for i in range(len(self.children)-4):
      self.children[i].label = self.cells_1[i]


  def next_button(self):
    # print(self.user_counter['Selected_Cells'])
    self.preserved_att = [[child.label, child.style, child.disabled]for child in self.children[:-4]]
    if self.preserved_att2 == []:
      for button, label in zip(self.children, self.cells_2):
        button.label = label
        button.style = discord.ButtonStyle.secondary
        button.disabled = False
      self.children[23].disabled = True
      self.children[20].disabled = False
    for child, (label, style, disabled) in zip(self.children, self.preserved_att2):
      child.label = label
      child.style = style
      child.disabled = disabled
    self.preserved_att2 = []
    self.children[23].disabled = True
    self.children[20].disabled = False
    if len(self.user_counter['Selected_Cells']) == 12:
      for i in self.children[:-4]:  #self.children[] is list of button instances
        i.disabled = True

  def previous_button(self):
    self.preserved_att2 = [[child.label, child.style, child.disabled]for child in self.children[:-4]]
    for child, (label, style, disabled) in zip(self.children, self.preserved_att):
      child.label = label
      child.style = style
      child.disabled = disabled
    self.preserved_att = []
    self.children[23].disabled = False
    self.children[20].disabled = True

  def reset_button(self):
    self.children[23].disabled = False
    self.embed.description = 'Create Build by simply selecting cells you want'
    if self.user_counter['Selected_Cells']:
      self.user_counter = {'Selected_Cells': [],self.user_id: [0] * 40}
      for button in self.children[:-4]:
        button.disabled = False
        button.style = discord.ButtonStyle.secondary
        if button.label.startswith('+'):
            button.label = button.label[2:]
      def reset_preserved_attributes(preserved_att):
        for attr in preserved_att:
          attr[1] = discord.ButtonStyle.secondary
          attr[2] = False
          if attr[0].startswith('+'):
              attr[0] = attr[0][2:]
      reset_preserved_attributes(self.preserved_att)
      reset_preserved_attributes(self.preserved_att2)



  def find_button(self):
    Perks_list = self.user_counter['Selected_Cells']
    Perks_list = [perk.strip() for perk in Perks_list]
    # print(Perks_list)
    result = Build_finder(Perks_list,self.language,self.weapon_type, self.weapon_filter, self.lantern, self.omnicell, 0)
    if result:
        self.build_icon_names, self.Build, self.total_combinations = result
    else:
        self.Build = []

  def button_click(self, button, index):
    label = button.label
    if self.children[23].disabled == False:
      index = index + 20
    if self.user_counter[self.user_id][index] < 1:
      self.user_counter['Selected_Cells'].append(label)
      self.user_counter[self.user_id][index] += 1
      button.style = discord.ButtonStyle.success
      button.label = f"+3 {label}"
      if len(self.user_counter['Selected_Cells']) == 12:
        for i in self.children[:-4]:  #self.children[] is list of button instances
          i.disabled = True
    else:
      self.user_counter['Selected_Cells'].append(label[3:])
      button.style = discord.ButtonStyle.success
      button.label = f"+6 {label[3:]}"
      button.disabled = True
      if len(self.user_counter['Selected_Cells']) == 12:
        for i in self.children[:-4]:
          i.disabled = True


  @discord.ui.button(label=cells_1[0], style=discord.ButtonStyle.secondary)
  async def button_1(self, interaction: discord.Interaction,button: discord.ui.Button):
    self.button_click(self.children[0], 0)
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label=cells_1[1], style=discord.ButtonStyle.secondary)
  async def button_2(self, interaction: discord.Interaction,
                     button: discord.ui.Button):
    self.button_click(self.children[1], 1)
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label=cells_1[2], style=discord.ButtonStyle.secondary)
  async def button_3(self, interaction: discord.Interaction,
                     button: discord.ui.Button):
    self.button_click(self.children[2], 2)
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label=cells_1[3], style=discord.ButtonStyle.secondary)
  async def button_4(self, interaction: discord.Interaction,
                     button: discord.ui.Button):
    self.button_click(self.children[3], 3)
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label=cells_1[4], style=discord.ButtonStyle.secondary)
  async def button_5(self, interaction: discord.Interaction,
                     button: discord.ui.Button):
    self.button_click(self.children[4], 4)
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label=cells_1[5], style=discord.ButtonStyle.secondary)
  async def button_6(self, interaction: discord.Interaction,
                     button: discord.ui.Button):
    self.button_click(self.children[5], 5)
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label=cells_1[6], style=discord.ButtonStyle.secondary)
  async def button_7(self, interaction: discord.Interaction,
                     button: discord.ui.Button):
    self.button_click(self.children[6], 6)
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label=cells_1[7], style=discord.ButtonStyle.secondary)
  async def button_8(self, interaction: discord.Interaction,
                     button: discord.ui.Button):
    self.button_click(self.children[7], 7)
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label=cells_1[8], style=discord.ButtonStyle.secondary)
  async def button_9(self, interaction: discord.Interaction,
                     button: discord.ui.Button):
    self.button_click(self.children[8], 8)
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label=cells_1[9], style=discord.ButtonStyle.secondary)
  async def button_10(self, interaction: discord.Interaction,
                      button: discord.ui.Button):
    self.button_click(self.children[9], 9)
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label=cells_1[10], style=discord.ButtonStyle.secondary)
  async def button_11(self, interaction: discord.Interaction,
                      button: discord.ui.Button):
    self.button_click(self.children[10], 10)
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label=cells_1[11], style=discord.ButtonStyle.secondary)
  async def button_12(self, interaction: discord.Interaction,
                      button: discord.ui.Button):
    self.button_click(self.children[11], 11)
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label=cells_1[12], style=discord.ButtonStyle.secondary)
  async def button_13(self, interaction: discord.Interaction,
                      button: discord.ui.Button):
    self.button_click(self.children[12], 12)
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label=cells_1[13],style=discord.ButtonStyle.secondary)
  async def button_14(self, interaction: discord.Interaction,
                      button: discord.ui.Button):
    self.button_click(self.children[13], 13)
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label=cells_1[14], style=discord.ButtonStyle.secondary)
  async def button_15(self, interaction: discord.Interaction,
                      button: discord.ui.Button):
    self.button_click(self.children[14], 14)
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label=cells_1[15], style=discord.ButtonStyle.secondary)
  async def button_16(self, interaction: discord.Interaction,
                      button: discord.ui.Button):
    self.button_click(self.children[15], 15)
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label=cells_1[16], style=discord.ButtonStyle.secondary)
  async def button_17(self, interaction: discord.Interaction,
                      button: discord.ui.Button):
    self.button_click(self.children[16], 16)
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label=cells_1[17], style=discord.ButtonStyle.secondary)
  async def button_18(self, interaction: discord.Interaction,
                      button: discord.ui.Button):
    self.button_click(self.children[17], 17)
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label=cells_1[18], style=discord.ButtonStyle.secondary)
  async def button_19(self, interaction: discord.Interaction,
                      button: discord.ui.Button):
    self.button_click(self.children[18], 18)
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label=cells_1[19], style=discord.ButtonStyle.secondary)
  async def button_20(self, interaction: discord.Interaction,
                      button: discord.ui.Button):
    self.button_click(self.children[19], 19)
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label='<',style=discord.ButtonStyle.primary,disabled=True)
  async def previous(self, interaction: discord.Interaction,
                     button: discord.ui.Button):
    self.previous_button()
    await interaction.response.edit_message(view=self)

  @discord.ui.button(label="Find Build", style=discord.ButtonStyle.success)
  async def Find_Build(self, interaction: discord.Interaction,button: discord.ui.Button):
    self.find_button()
    if self.Build == []:
      view = self
      self.embed.description = ui_text[self.language]['noBuildFound']
      await interaction.response.edit_message(embed=self.embed, view=view)
    else:
      Perks_list = self.user_counter['Selected_Cells']
      Perks_list = [perk.strip() for perk in Perks_list]
      view = PostBuild(self.build_icon_names,Perks_list,self.Build,self.total_combinations,self.language)
      img_generator(self.build_icon_names,Perks_list,self.Build,0)
      await interaction.response.send_message(content=f"{ui_text[self.language]['totalCombinations']}: {1}-{self.total_combinations}",
        view=view, file=discord.File("build_img.png"),ephemeral=True)

  @discord.ui.button(label="Reset", style=discord.ButtonStyle.danger)
  async def Reset(self, interaction: discord.Interaction,
                  button: discord.ui.Button):
    self.reset_button()
    await interaction.response.edit_message(embed=self.embed,view=self)

  @discord.ui.button(label=">", style=discord.ButtonStyle.primary)
  async def next(self, interaction: discord.Interaction,button: discord.ui.Button):
    self.next_button()
    await interaction.response.edit_message(view=self)

class RecruitForm(discord.ui.Modal, title='Recruitment Form'):
  def __init__(self,Username):
    super().__init__()
    self.discord_name = Username

  ign = discord.ui.TextInput(label="What is your IGN?",style=discord.TextStyle.short)
  platform = discord.ui.TextInput(label="What platform you play on?",style=discord.TextStyle.short)
  region = discord.ui.TextInput(label="What is your Region?",style=discord.TextStyle.short)
  requirnment = discord.ui.TextInput(label="Can you Solo Heroic Escalation under 30 min?",style=discord.TextStyle.short)

  async def on_submit(self,interaction: discord.Interaction):
    # print(self.discord_name)
    await interaction.response.defer()