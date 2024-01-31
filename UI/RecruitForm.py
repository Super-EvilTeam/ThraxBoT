import discord
import re

class RecruitForm(discord.ui.Modal, title="Recruitment Form"):
  basic = discord.ui.TextInput(row=0,label= "IGN/Platform/Region",placeholder='eg. SuperEvilTeam/PC/SEA',required=True,style=discord.TextStyle.short)
  playtime = discord.ui.TextInput(label= "How many hours you have in game?",placeholder='eg. 100+, 500+, 1000+, 2000+',required=True,style=discord.TextStyle.short)
  Hesca = discord.ui.TextInput(label= "Can you Solo Heroic Escalation under 30 min?",placeholder='Yes/No',required=True,style=discord.TextStyle.short)
  Titles = discord.ui.TextInput(label= "Which Trials/Gauntlet Titles you have?",placeholder='eg. The Dauntless,The Gauntless, Trials Champion, Hammer Champion etc',required=False,style=discord.TextStyle.long)

  async def on_submit(self, interaction: discord.Interaction):
    # Validate the 'basic' input format
    basic_input = self.basic.value
    if not validate_basic_input(basic_input):
        # If the input is not in the proper format, send an error message to the user
        await interaction.response.send_message(f"   {self.basic.value}           <------\n\nError: Please enter the 'IGN/Platform/Region' in the correct format (e.g., SuperEvilTeam/PC/SEA).", ephemeral=True)
        return
    await interaction.response.send_message(f"Thank you for Applying to Guild {interaction.user.mention}, Officers will check it and reach out to you!",ephemeral=True)
    channel = discord.utils.get(interaction.guild.channels,name = "recruitment-applications")
    await channel.send(
      f"Application submitted by {interaction.user.mention} \n\nBasic Info: {self.basic} \nPlaytime: {self.playtime} \nHesca Under 30: {self.Hesca} \nTitles: {self.Titles}")
    
def validate_basic_input(basic_input):
    # Define the pattern for the format "string/string/string"
    pattern = re.compile(r'^\s*\w+(\s*\w*)*/\s*\w+\s*/\s*\w+\s*$')  # This pattern assumes alphanumeric characters and underscores

    # Check if the input matches the pattern
    if pattern.match(basic_input):
        return True
    else:
        return False