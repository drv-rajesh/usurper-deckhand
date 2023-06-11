import discord
from discord import app_commands
from discord.ext import commands

from math import ceil, floor
from csv import reader

class Reputation(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot
    with open("settings.csv") as f:
      settings = list(reader(f))
    self.ephemeral = {"Ephemeral": True, "Permanent": False}[settings[0][1]]
    self.multiplier = float(settings[1][0].replace("x",""))

  @app_commands.command(name="milestones", description="Generates rep commands based on met clan XP milestones")
  @app_commands.describe(helpers="Comma-separated indexes (from top of scoreboard, starting from 0) of helpers (e.g. 0,2,5,6)")
  @app_commands.describe(multipliers="Comma-separated indexes (from top of scoreboard, starting from 0) of players receiving a multiplier (e.g. 0,2,5,6)")
  async def milestones(self, interaction: discord.Interaction, helpers: str = "None", multipliers: str = "None"):
    history = [message async for message in interaction.channel.history(limit=1)]
    board = [embed.to_dict() for embed in history[0].embeds if "Weekly Clan XP Gains:" in embed.title]
    helpers = [int(helper) for helper in helpers.split(",") if helper != "None"]
    multipliers = [int(receive) for receive in multipliers.split(",") if receive != "None"]
  
    entries = board[0]["description"].split("\n")[1:-3]
    reps = []
  
    with open("milestones.csv") as f:
      milestones = list(reader(f, delimiter="|"))
      top = True
      for entry in range(len(entries)):
        root = entries[entry].split(" - ") 
        xp = int(root[1].replace(",", ""))
        
        minreached = False
        for milestone in range(len(milestones)):
          if int(milestones[milestone][0]) > xp and not minreached:
            if int(milestones[milestone-1][0]) > 0:
              repamt = int(milestones[milestone-1][1])
              if top: repamt += 10
              if entry in helpers: repamt += 2
              if entry in multipliers:
                with open("settings.csv") as f:
                  settings = list(reader(f)) 
                  if settings[2][1] == "ceil":
                    repamt = ceil(repamt*self.multiplier)
                  elif settings[2][1] == "floor":
                    repamt = floor(repamt*self.multiplier)
              reps.append({f'@{root[0].replace("*", "")}': str(repamt)})
            minreached = True
        top = False
    
    cmds = "\n".join([f"/giverep user:{list(rep.keys())[0]} num:{rep[list(rep.keys())[0]]}" for rep in reps])
    await interaction.response.send_message(cmds, ephemeral=self.ephemeral)
  
  @app_commands.command(name="qotd", description="Generates rep commands for QOTD responses")
  @app_commands.describe(react="Reacts to every message accounted for (e.g. True)")
  @app_commands.describe(multipliers="Comma-separated values of the username and discriminant of multiplier receivers (e.g. user#5678,user#3789)")
  async def qotd(self, interaction: discord.Interaction, react: str = "False", multipliers: str = "None"):
    history = [message async for message in interaction.channel.history(limit=100)]
    responses = [[f"{message.author.name}#{message.author.discriminator}", message.content] for message in history]
    multipliers = [receive for receive in multipliers.split(",") if receive != "None"]

    with open("settings.csv") as f:
      settings = list(reader(f)) 
    
    maxhistory = False
    users = []
    for message in responses:
      if "NEW QOTD" in message[1]:
        maxhistory = True
      if not maxhistory:
        users.append(message[0])
        
    if react == "True":
      for message in history[:len(users)]:
        await message.add_reaction({"checkmark": "\U00002705", "thumbs up": "\U0001F44D", "eyes": "\U0001F440"}[settings[3][0]])
    
    users = set(users)
    cmds = ""
    for user in users:
      cmds = "\n".join([f"/giverep user:{user} num:{1}" for user in users])
      if user in multipliers:
          if settings[2][1] == "ceil":
            cmds = "\n".join([f"/giverep user:{user} num:{ceil(1*self.multiplier)}" for user in users])
          elif settings[2][1] == "floor":
            cmds = "\n".join([f"/giverep user:{user} num:{floor(1*self.multiplier)}" for user in users])
    await interaction.response.send_message(cmds, ephemeral=self.ephemeral)

async def setup(bot):
  await bot.add_cog(Reputation(bot), guilds=[discord.Object(1107763811823403098)])
