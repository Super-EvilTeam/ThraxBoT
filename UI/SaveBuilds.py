import discord
from build_finder import img_generator,load_json
from UI.MetaBuilds import generate_options

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
      self.mod =  self.saved_builds[self.user_id][select.values[0]]["Mod"]
      self.special = self.saved_builds[self.user_id][select.values[0]]["Special"]
      self.tonics = self.saved_builds[self.user_id][select.values[0]]["Tonics"]
      self.img = img_generator([self.Icons],self.Perks,0,0,self.mod,self.special,self.tonics)
      self.post_build.disabled = False
      self.post_build.style = discord.ButtonStyle.success
      await interaction.response.edit_message(attachments=[discord.File(self.img, filename='image.png')],view = self)
   
   @discord.ui.button(label="Post Build")
   async def post_build(self,interaction,button):
      self.img = img_generator([self.Icons],self.Perks,0,0,self.mod,self.special,self.tonics)
      await interaction.channel.send(file=discord.File(self.img, filename='image.png'))
      await interaction.response.defer()