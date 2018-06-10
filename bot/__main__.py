from discord.ext.commands import Bot, when_mentioned_or
from discord import Game

from os import environ


muted = []
admins = []

bot = Bot(
    command_prefix=when_mentioned_or(
        "...", ":"
    ),
    activity=Game(
        name=":help"
    )
)

bot.muted = []

bot.banned_ids = []

@bot.check
async def block_banned_ids(ctx):
    return ctx.author.id not in bot.banned_ids

@bot.check
async def block_muted(ctx):
    return ctx.author.id not in bot.muted


bot.load_extension("bot.cogs.admin")
bot.load_extension("bot.cogs.general")
bot.load_extension("bot.cogs.cyber")
bot.load_extension("bot.cogs.fun")


bot.run(environ.get("BOT_TOKEN"))

####### ------------------------------------

####### ------------------------------------

"""
##REACT STUFF V2:
###ADD CUSTOM ReACTIONS
@bot.listen()
async def on_message(message):
    text = (message.content).lower()
    if text.startswith(":react"):
        if str(message.author.id) in banned_ids: await bot.send_message(message.channel,message.author.mention+"  is banned from (ab)using this bot.");return ""
        print(str(message.author)+" reacted with: "+text.replace(":react ",""))
        try:
            channel = bot.get_channel(str(450066374824558613))
            await bot.send_message(channel, (str(message.author).replace("@","")) +" reacted with: "+(text.replace(":react ",""))[1:])
        except:
            pass
        chan = message.channel; auth = str(message.author.mention)
        text = text.split(" ")
        try: await bot.delete_message(message)
        except: pass
        try: num = int(text[1])-1;actual_text = ' '.join(text[2:])
        except: num = 0;actual_text = ' '.join(text[1:])
        mgs = []
        async for x in bot.logs_from(chan,limit = num+1): mgs.append(x)
        foundmessage = mgs[num]
        if len(foundmessage.reactions) > 19:
            msg = await bot.send_message(chan,auth+"  |  Maximum reactions added (**20**)!")
            await asyncio.sleep(4)
            await bot.delete_message(msg)
        for long in LONG_CHARS:
            if (long in actual_text): actual_text = actual_text.replace(long,LONG_CHARS[long],1)
        used = ""
        for char in actual_text:
            if char in CHARS:
                try:
                    actual_text = actual_text.replace(char,CHARS[char][used.count(char)],1)
                except IndexError:
                    pass
                used += char
        used = ""
        for char in actual_text:
            try:
                if (char not in used) and (char in "0123456789"): await bot.add_reaction(foundmessage,NUMS[int(char)*2]);used += char
                elif (char in used) and (char in "0123456789"): await bot.add_reaction(foundmessage,NUMS[(int(char)*2)+1][used.count(char)-1]);used += char
                else: await bot.add_reaction(foundmessage,char)
            except discord.errors.HTTPException as ex:
                if "Unknown Emoji" in str(ex):
                    continue
                elif "Maximum number of reactions reached" in str(ex):
                    msg = await bot.send_message(chan,auth+"  |  Maximum reactions added (**20**)!")
                    await asyncio.sleep(7)
                    await bot.delete_message(msg)
                    break
                else: print(ex)




"""