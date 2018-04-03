import discord
from discord.ext import commands
import asyncio
desc = ""
bot = commands.Bot(command_prefix='...', description=desc)

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    while True:
        out = input("What do you want to say: ")
        if out != "":
            await bot.send_message(discord.Object(id="413755435338956811"),out)

bot.run('NDI5NzUwNTI5NzM2ODM1MDc0.DaQ1pg.AZkv3BTcOAWHCc_QN0E83bZdXOs')
