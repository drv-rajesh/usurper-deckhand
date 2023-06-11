import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import View

from csv import reader, writer

#embeds
def main_panel():
  main_panel = discord.Embed(title="Administrator Console", description="**!reload after changing a setting** (values may not visually update, despite actually updating. close and re-enter menu for **visual** updates)", color=0xeb2352)
  main_panel.set_thumbnail(url="https://i.imgur.com/JOLLl8i.png")
  main_panel.add_field(name="General", value="Bot customization (e.g. ephemeral responses)", inline=False)
  main_panel.add_field(name="Commands", value="Command documentation", inline=False)
  main_panel.add_field(name="Experimental", value="Rep update features (e.g. multipliers)", inline=False)
  return main_panel

def general_panel():
  general_panel = discord.Embed(title="General", description="**!reload after changing a setting** (values may not visually update, despite actually updating. close and re-enter menu for **visual** updates)", color=0xeb2352)
  general_panel.set_thumbnail(url="https://i.imgur.com/JOLLl8i.png")
  general_panel.add_field(name="Ephemeral", value="Enables ephemeral responses (visible only to person entering the command)", inline=False)
  general_panel.add_field(name="Reaction", value="Changes QOTD response reaction", inline=False)
  return general_panel

def commands_panel():
  commands_panel = discord.Embed(title="Commands", description="**!reload after changing a setting** (values may not visually update, despite actually updating. close and re-enter menu for **visual** updates)", color=0xeb2352)
  commands_panel.set_thumbnail(url="https://i.imgur.com/JOLLl8i.png")
  commands_panel.add_field(name="\u200b", value="**Utility**", inline=False)
  commands_panel.add_field(name="!sync", value="Syncs bot commands to current guild.", inline=False)
  commands_panel.add_field(name="!reload", value="Reloads bot extensions. Necessary after changing a setting.", inline=False)
  commands_panel.add_field(name="!ping", value="Displays Discord WebSocket protocol latency.", inline=False)
  commands_panel.add_field(name="\u200b", value="**Features**", inline=False)
  commands_panel.add_field(name="/console", value="Opens bot administrator console.", inline=False)
  commands_panel.add_field(name="/milestones", value="Generates rep commands based on met clan XP milestones.\n**args**: \n[helpers (str), comma-separated indexes, starting from 0 (top of scoreboard), e.g. 0,2,5,6, default='None']\n[multipliers (str), comma-separated indexes, starting from 0 (top of scoreboard), e.g. 0,2,5,6, default='None']", inline=False)
  commands_panel.add_field(name="/qotd", value="Generates rep commands for QOTD responses.\n**args**: \n[react (str), True/False, e.g. True, default='False']\n[multipliers (str), comma-separated identifiers (username#discriminator), e.g. user#1234,user2#5678, default='None']", inline=False)
  return commands_panel

def experimental_panel():
  experimental_panel = discord.Embed(title="Experimental", description="**!reload after changing a setting** (values may not visually update, despite actually updating. close and re-enter menu for **visual** updates)", color=0xeb2352)
  experimental_panel.set_thumbnail(url="https://i.imgur.com/JOLLl8i.png")
  experimental_panel.add_field(name="Multiplier", value="Change the rep earned multiplier", inline=False)
  experimental_panel.add_field(name="Multiplier Rounding", value="Change rounding of multiplier calculations (e.g. ceil 1.5\*1 = 2, floor 1.5\*1 = 1)", inline=False)
  return experimental_panel
  
#views
class MainView(View):
  @discord.ui.button(label="General", style=discord.ButtonStyle.blurple)
  async def general_callback(self, interaction, button):
    await interaction.response.edit_message(embed=general_panel(), view=GeneralView())
  
  @discord.ui.button(label="Commands", style=discord.ButtonStyle.blurple)
  async def commands_callback(self, interaction, button):
    await interaction.response.edit_message(embed=commands_panel(), view=CommandsView())
  
  @discord.ui.button(label="Experimental", style=discord.ButtonStyle.red)
  async def experimental_callback(self, interaction, button):
    await interaction.response.edit_message(embed=experimental_panel(), view=ExperimentalView())

class GeneralView(View):
  with open("settings.csv") as f:
    settings = list(reader(f))
  button_colour = {"green": discord.ButtonStyle.success, "red": discord.ButtonStyle.danger}[settings[0][0]]
  
  @discord.ui.button(label=settings[0][1], style=button_colour)
  async def ephemeral_callback(self, interaction, button):
    with open("settings.csv") as f:
      settings = list(reader(f))
    button_colour = {"green": discord.ButtonStyle.danger, "red": discord.ButtonStyle.success}[settings[0][0]]
    state = {"Ephemeral": "Permanent", "Permanent": "Ephemeral"}[settings[0][1]]
    button.style = button_colour
    button.label = state

    override = {0:[{"ButtonStyle.success": "green", "ButtonStyle.danger": "red"}[str(button_colour)], state]}
    with open("settings.csv", "w") as f:
      modified = writer(f)
      for line, row in enumerate(settings):
        data = override.get(line, row)
        modified.writerow(data)
    await interaction.response.edit_message(view=self)

  @discord.ui.select(placeholder=f"Reaction: {settings[3][0]}", options=[
      discord.SelectOption(label="checkmark", emoji="\U00002705"),
      discord.SelectOption(label="thumbs up", emoji="\U0001F44D"),
      discord.SelectOption(label="eyes", emoji="\U0001F440")
  ])
  async def select_callback(self, interaction, select):
    with open("settings.csv") as f:
      settings = list(reader(f))
      
    override = {3:[select.values[0], "None"]}
    with open("settings.csv", "w") as f:
      modified = writer(f)
      for line, row in enumerate(settings):
        data = override.get(line, row)
        modified.writerow(data)
    await interaction.response.edit_message(view=self)
    
  @discord.ui.button(label="Back", style=discord.ButtonStyle.gray)
  async def back_callback(self, interaction, button):
    await interaction.response.edit_message(embed=main_panel(), view=MainView())

class CommandsView(View): 
  @discord.ui.button(label="Back", style=discord.ButtonStyle.gray)
  async def back_callback(self, interaction, button):
    await interaction.response.edit_message(embed=main_panel(), view=MainView())

class ExperimentalView(View):
  with open("settings.csv") as f:
    settings = list(reader(f))
  
  @discord.ui.select(placeholder=f"Multiplier: {settings[1][0]}", options=[
      discord.SelectOption(label="1x"),
      discord.SelectOption(label="1.25x"),
      discord.SelectOption(label="1.5x"),
      discord.SelectOption(label="2x")
  ])
  async def select_callback(self, interaction, select):
    with open("settings.csv") as f:
      settings = list(reader(f))
      
    override = {1:[select.values[0], "None"]}
    with open("settings.csv", "w") as f:
      modified = writer(f)
      for line, row in enumerate(settings):
        data = override.get(line, row)
        modified.writerow(data)
    await interaction.response.edit_message(view=self)

  button_colour = {"green": discord.ButtonStyle.success, "red": discord.ButtonStyle.danger}[settings[2][0]]
  @discord.ui.button(label=settings[2][1], style=button_colour)
  async def round_callback(self, interaction, button):
    with open("settings.csv") as f:
      settings = list(reader(f))
    button_colour = {"green": discord.ButtonStyle.danger, "red": discord.ButtonStyle.success}[settings[2][0]]
    round = {"ceil": "floor", "floor": "ceil"}[settings[2][1]]
    button.style = button_colour
    button.label = round

    override = {2:[{"ButtonStyle.success": "green", "ButtonStyle.danger": "red"}[str(button_colour)], round]}
    with open("settings.csv", "w") as f:
      modified = writer(f)
      for line, row in enumerate(settings):
        data = override.get(line, row)
        modified.writerow(data)

    await interaction.response.edit_message(view=self)
    
  @discord.ui.button(label="Back", style=discord.ButtonStyle.gray)
  async def back_callback(self, interaction, button):
    await interaction.response.edit_message(embed=main_panel(), view=MainView())

class Console(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot

  @commands.command()
  async def sync(self, ctx):
    await ctx.bot.tree.sync(guild=ctx.guild)
    await ctx.send("Synced commands to current guild.")

  @commands.command()
  async def reload(self, ctx):
    await ctx.bot.reload_extension("console")
    await ctx.bot.reload_extension("reputation")
    await ctx.send("Reloaded all extensions.")

  @commands.command()
  async def ping(self, ctx):
    await ctx.send(f"Discord WebSocket protocol latency is {round(ctx.bot.latency*1000, 2)} ms.")
    
  @app_commands.command(name="console", description="Opens bot administrator console")
  async def console(self, interaction: discord.Interaction):
    await interaction.response.send_message(embed=main_panel(), view=MainView())

async def setup(bot):
  await bot.add_cog(Console(bot), guilds=[discord.Object(1107763811823403098)])
