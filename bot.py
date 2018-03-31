import discord
import urllib.parse
from discord.ext import commands
import requests as rq
desc = "test"
bot = commands.Bot(command_prefix='...', description=desc)

##TELLS ME I'VE LOGGED IN
@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')


##CONTROVERSIAL FILTER
contrv = [listofbadwordsthativeremoved]
@bot.listen()
async def on_message(message):
    text = message.content
    if (any(x in text.lower() for x in contrv)) and (str(message.author) != "Cyber Discovery Bot#7995"):
        await bot.send_message(message.channel, message.author.mention+"  |  *Please refrian from discussing controversial topics in this discord, **as mentioned in rule 2**.\nThis includes discussion of race, religion, politics, gender and sexuality.*")



##WHOPINGED/debato
@bot.listen()
async def on_message(message):
    text = message.content
    if ("@everyone" in text.lower()) or ("@here" in text.lower()):
        reaction_list = ["🙁","🇼","🇭","🇴","🔵","🇵","🇮","🇳","🇬","🇪","🇩"]
        for x in reaction_list: await bot.add_reaction(message,x)
    elif "dabato" in text.lower():
        await bot.add_reaction(message,"🤔")

##LMGTFY
@bot.listen()
async def on_message(message):
    text = message.content
    if text.startswith('.lmgtfy'):
        if message.mentions:
            for x in message.mentions: text = text.replace(str(x.mention),"")
            url = "https://lmgtfy.com/?q="+urllib.parse.quote_plus(text[9:])
            url = "  |  " +rq.get("http://tinyurl.com/api-create.php?url="+url).text
            await bot.send_message(message.channel,message.mentions[0].mention+url)
        else:
            url = "https://lmgtfy.com/?q="+urllib.parse.quote_plus(text[8:])
            url = rq.get("http://tinyurl.com/api-create.php?url="+url).text
            await bot.send_message(message.channel,url)

###ADD CUSTOM ReACTIONS
@bot.listen()
async def on_message(message):
    text = (message.content).lower()
    if message.content.startswith('.react'):
        text = text.split(" ")
        try:
            num = int(text[1])
        except ValueError:
            await bot.send_message(message.channel,str(message.author.mention)+"  |  Correct syntax: `.react <number of messages up to react to> <text>` (e.g. `.react 1 abc`).")
            return ""
        mgs = []
        async for x in bot.logs_from(message.channel,limit = num+1):
            mgs.append(x)
        foundmessage = mgs[num]
        actual_text = ' '.join(text[2:])
        regional_chars = "🇦 🇧 🇨 🇩 🇪 🇫 🇬 🇭 🇮 🇯 🇰 🇱 🇲 🇳 🇴 🇵 🇶 🇷 🇸 🇹 🇺 🇻 🇼 🇽 🇾 🇿 ◽".split(" ")
        repeat_chars = "🅰 🅱 © 🇩 🇪 🇫 🇬 🇭 ℹ 🗾 🇰 🇱 Ⓜ ♑ 🅾 🅿 🇶 ® 🇸 🇹 ♉ 🇻 🇼 ✖️ 🇾 💤 ⚪".split(" ")
        numbers = "0⃣ 1⃣ 2⃣ 3⃣ 4⃣ 5⃣ 6⃣ 7⃣ 8⃣ 9⃣ 🔟".split(" ")
        empt = ""
        for char in actual_text:
            if char == " ": char = "{"
            if char in "0123456789":
                await bot.add_reaction(foundmessage,numbers[int(char)])
                continue
            try: newchar = regional_chars[ord(char)-97]
            except: newchar=regional_chars[26]
            if newchar in empt:
                try: newchar = repeat_chars[ord(char)-97]
                except: newchar = repeat_chars[26]
            empt += newchar
            try: await bot.add_reaction(foundmessage,newchar)
            except discord.errors.Forbidden: await bot.send_message(message.channel,str(message.author.mention)+"  |  Too many reactions!")
            except discord.errors.HTTPException: pass
        await bot.delete_message(message)

@bot.listen()
async def on_message(message):
    text = (message.content).lower().replace(":","")
    if message.content.startswith(':'):
        inp = text.split("c")
        for count,x in enumerate(inp): inp[count] = int(x.replace("l",""))-1
        with open('/home/main/headquarters.txt') as f:
            text = (f.read()).split(";;;;;;")
        text = text[inp[0]]
        text = text.split(":::")
        try:
            text = text[inp[1]]
        except:
            await bot.send_message(message.channel,str(message.author.mention)+"  |  ")
            return ""
        await bot.send_message(message.channel,text)

@bot.listen()
async def on_message(message):
    url = "https://haveibeenpwned.com/api/v2/breachedaccount/"
    if message.content.startswith(":haveibeenpwned"):
        text = (message.content).replace(":haveibeenpwned ","")
        r = rq.get(url+text)
        await bot.send_message(message.channel,r.text)




bot.run(apikey)
