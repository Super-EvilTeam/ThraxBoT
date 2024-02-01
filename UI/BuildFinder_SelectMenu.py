import discord
from UI.BuildFinder_Cells import SimpleView
from build_finder import load_json

text_data = load_json('Text_data.json')
ui_text = load_json('UI_text.json')

EMOJI = {"weapon_type":['<:as:1192842658343817226>',
                        '<:axe:1192852193229934663>',
                        '<:cb:1192850297563914271>',
                        '<:hammer:1192852188767195237>',
                        '<:repeater:1192852181683019907>',
                        '<:sword:1192846249804697692>',
                        '<:pike:1192852184245751808>'],
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

def generate_options(option,language,emoji=False):
  if emoji:
    return [discord.SelectOption(label=option,emoji=EMOJI[emoji][i],value=option) for i, 
            option in enumerate(text_data[option][language])]
  return [discord.SelectOption(label=option,value=option) for i, option in enumerate(text_data[option][language])]

class SelectMenu(discord.ui.View):

  def __init__(self,embed,language,user_id):
    super().__init__()
    self.user_id = user_id
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
      view = SimpleView(self.user_id, embed, self.weapon_type, self.weapon_filter,self.omnicell,self.lantern,self.language)
      await interaction.response.edit_message(view=view,embed=embed)