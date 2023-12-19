import os
import discord
from discord.ext import commands
from build_finder import Build_finder
from build_finder import img_generator
from build_finder import translate_to_english
import json
from server import keep_alive
from dotenv import load_dotenv

user_id = None
mods = None


EMOJI = {"weapon_type":['<:AetherStrikers:1171706545323651083>',
                   '<:Axe:1171720563207708733>',
                   '<:ChainBlades:1171720566839971910>',
                   '<:Hammer:1171720570711330876>',
                   '<:Repeater:1171720590135132172>',
                   '<:Sword:1171720593767403520>',
                   '<:WarPike:1171720599823990824>'],
        "omnicell":["<:RevenantAbility:1174970642316136528>",
                    "<:DisciplineAbility:1174970622812631041>",
                    "<:BastionAbility:1174970614000390216>",
                    "<:TempestAbility:1174970651656847450>",
                    "<:ArtificerAbility:1174970606605840444>",
                    "<:IceborneAbility:1174970634242105364>"],
        "lanterns":["<:BroadsidesLantern:1174973817911775273>",
                   "<:DrasksEye:1174973820461912074>",
                   "<:EmbermanesRapture:1174973824236802078>",
                   "<:KoshaisBloom:1174973828305276969>",
                   "<:PangarsShine:1174973832537325629>",
                   "<:RecruitsLantern:1174973836635152394>",
                   "<:ShrikesZeal:1174973839298527242>",
                   "<:SkarnsDefiance:1174973841752207370>"]}


def load_json(filename):
  with open(filename, 'r') as file:
      data = json.load(file)
      return data

text_data = load_json('src\\json\\Text_data.json')
ui_text = load_json('src\\json\\UI_text.json')

def generate_options(option,language,emoji=False):
  if emoji:
    return [discord.SelectOption(label=option,emoji=EMOJI[emoji][i],value=option) for i, 
            option in enumerate(text_data[option][language])]
  return [discord.SelectOption(label=option,value=option) for i, option in enumerate(text_data[option][language])]

class SelectLanguage(discord.ui.View):
  def __init__(self):
    super().__init__()

  def button_click(self,label):
    embed = discord.Embed(colour=0xC934EB,title='Build Finder',description=ui_text[label]["createBuild"])
    view = SelectMenu(embed,label)
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

class post_build(discord.ui.View):
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

class SelectMenu(discord.ui.View):

  def __init__(self,embed,language):
    super().__init__()
    self.embed = embed
    self.weapon_type = None
    self.weapon_filter = None
    self.lantern = None
    self.omnicell = None
    self.language = language
    self.select_weapon_type.options=generate_options("WEAPONS_OPTIONS",language,emoji="weapon_type")
    self.select_weapon.options = generate_options("BEHEMOTH_OPTIONS",language)
    self.select_omnicell.options = generate_options("OMNICELLS",language,emoji ="omnicell")
    self.select_lantern.options = generate_options("LANTERNS_OPTIONS",language,emoji="lanterns")
    self.select_weapon_type.placeholder = ui_text[self.language]["selectWeaponType"]
    self.select_weapon.placeholder = ui_text[self.language]["selectWeapon"]
    self.select_omnicell.placeholder = ui_text[self.language]["selectOmnicell"]
    self.select_lantern.placeholder = ui_text[self.language]["selectLantern"]


  @discord.ui.select()
  async def select_weapon_type(self, interaction, select):
    idx = text_data["WEAPONS_OPTIONS"][self.language].index(select.values[0])
    self.weapon_type = text_data["WEAPONS_OPTIONS"]["english"][idx]
    # print(self.weapon_type)
    await interaction.response.defer()

  @discord.ui.select()
  async def select_weapon(self, interaction, select):
    idx = text_data["BEHEMOTH_OPTIONS"][self.language].index(select.values[0])
    self.weapon_filter = text_data["BEHEMOTH_OPTIONS"]["english"][idx]
    # print(self.weapon_filter)
    await interaction.response.defer()

  @discord.ui.select()
  async def select_omnicell(self, interaction, select):
    idx = text_data["OMNICELLS"][self.language].index(select.values[0])
    self.omnicell = text_data["OMNICELLS"]["english"][idx]
    # print(self.omnicell)
    await interaction.response.defer()

  @discord.ui.select()
  async def select_lantern(self, interaction, select):
    idx = text_data["LANTERNS_OPTIONS"][self.language].index(select.values[0])
    self.lantern = text_data["LANTERNS_OPTIONS"]["english"][idx]
    # print(self.lantern)
    await interaction.response.defer()

  @discord.ui.button(label="Confirm", style=discord.ButtonStyle.success)
  async def Confirm(self, interaction: discord.Interaction,button: discord.ui.Button):
    if self.weapon_type is None or self.weapon_filter is None or self.lantern is None or self.omnicell is None:
      self.embed.description = "Please select a weapon type, weapon filter, lantern and omnicell."
      await interaction.response.edit_message(view=self,embed =self.embed)
    else:
      embed = discord.Embed(colour=0xC934EB,title='Build Finder',description=ui_text[self.language]["createBuild"])
      embed.add_field(name="Weapon Type",value=self.weapon_type)
      embed.add_field(name="Weapon",value=self.weapon_filter)
      embed.add_field(name="Omnicell",value=self.omnicell)
      embed.add_field(name="Lantern",value=self.lantern)
      view = SimpleView(user_id, embed, self.weapon_type, self.weapon_filter,self.omnicell,self.lantern,self.language)
      await interaction.response.edit_message(view=view,embed=embed)

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
      view = post_build(self.build_icon_names,Perks_list,self.Build,self.total_combinations,self.language)
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
    view_menu = SelectLanguage()
    await interaction.response.send_message(embed=embed,view=view_menu,ephemeral=True)

  # @bot.tree.command(name="recruit")
  # async def recruit(interaction: discord.Interaction):
  #   Username = interaction.user.name
  #   modal = RecruitForm(Username)
  #   await interaction.response.send_modal(modal)

  keep_alive()
  bot.run(my_secret)