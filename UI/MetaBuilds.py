import discord
from build_finder import load_json,img_generator

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

weapons = ["Aether Strikers", "Axe", "Chain Blades", "Hammer", "Repeater", "Sword", "War Pike"]
omnicell = ["Revenant", "Discipline", "Bastion", "Tempest", "Artificer", "Iceborne"]
element = ["Frost","Blaze","Shock","Terra","Umbral","Radiant"]
meta_builds_data = load_json("Meta_builds.json")

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

def generate_options(option_list,emoji=False):
    if emoji:
        options = [discord.SelectOption(label=weapon,value=weapon, emoji=emoji[index]) for index, weapon in enumerate(option_list)]
    else:
       options = [discord.SelectOption(label=weapon,value=weapon) for index, weapon in enumerate(option_list)]
    return options